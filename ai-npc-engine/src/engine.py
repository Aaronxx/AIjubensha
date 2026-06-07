"""AI NPC Dialogue Engine — dual-call with fabrication guard."""
from __future__ import annotations

from dataclasses import dataclass, field

from .llm_client import LLMClient
from .models import GamePhase, NPCDefinition, NPCState, SilenceStrategy
from .prompt import (
    ContextAssembler,
    DialoguePromptBuilder,
    ExtractionAssembler,
    ExtractionPromptBuilder,
    OutputParser,
    SILENCE_HINTS,
)
from .state_manager import StateManager

# Stock evasion templates per silence strategy — used when fabrication is detected
EVASION_TEMPLATES: dict[SilenceStrategy, list[str]] = {
    SilenceStrategy.HARD_SILENCE: [""],
    SilenceStrategy.POLITE_REFUSAL: [
        "关于这个...我不想多谈。",
        "这件事还是改日再聊吧。",
        "抱歉，这个问题我不太想回答。",
    ],
    SilenceStrategy.DEFLECT: [
        "这个你应该去问别人，我帮不了你。",
        "我不清楚这些，或许你问问其他人？",
    ],
    SilenceStrategy.CHANGE_SUBJECT: [
        "说起来...今天天气倒是不错。",
        "要再来一杯茶吗？",
        "你看这幅画的光影，多美。",
    ],
    SilenceStrategy.EMOTIONAL_AVOIDANCE: [
        "（沉默了很久，眼眶微红）",
        "（手指微微颤抖，别过头去）",
        "（深吸一口气，却什么也没说）",
    ],
}


@dataclass
class NPCReply:
    npc_id: str
    npc_name: str
    reply_text: str
    emotional_tag: str
    info_revealed: list[dict]
    attitude_shift: str | None
    arc_state_transition: str | None
    dialogue_latency_ms: float
    extraction_latency_ms: float
    tokens_used: int
    fabrication_detected: bool = False
    original_reply: str = ""


class NPCsEngine:
    """Core engine: dialogue → extraction → fabrication guard → state update."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()
        self.assembler = ContextAssembler()
        self.extraction_assembler = ExtractionAssembler()
        self.dialogue_builder = DialoguePromptBuilder()
        self.extraction_builder = ExtractionPromptBuilder()
        self.parser = OutputParser()
        self.state_mgr = StateManager()
        self._last_trigger_negative = False  # For cumulative effect tracking

    async def process_player_message(
        self,
        npc_def: NPCDefinition,
        npc_state: NPCState,
        player_id: str,
        player_message: str,
        phase: GamePhase,
        recent_messages: list[dict],
        topic_in_lie_range: bool = False,
    ) -> NPCReply:
        # ── Call 1: Generate natural dialogue ──
        arc_state = self.assembler.get_arc_state(npc_def, npc_state)
        dialogue_ctx = self.assembler.build_dialogue_context(
            npc_def, npc_state, phase, player_message, recent_messages, arc_state
        )
        dialogue_sys, dialogue_user = self.dialogue_builder.build(dialogue_ctx)
        dialogue_resp = await self.llm.chat(dialogue_sys, dialogue_user, temperature=0.85)
        reply_text = dialogue_resp.raw_text.strip()

        # ── Call 2: Extract metadata ──
        extraction_ctx = self.extraction_assembler.build(
            npc_def, npc_state, reply_text, player_message, recent_messages
        )
        extraction_sys, extraction_user = self.extraction_builder.build(extraction_ctx)
        extraction_resp = await self.llm.chat(
            extraction_sys, extraction_user, temperature=0.3, max_tokens=300
        )
        parsed = self.parser.parse(
            extraction_resp.raw_text, fallback_emotional_tag=npc_state.emotional_tag
        )

        # ── Fabrication guard: detect and correct ──
        corrected, original = self._guard_fabrication(
            parsed, reply_text, npc_def, npc_state
        )
        if corrected:
            reply_text = corrected

        # ── Deterministic attitude triggers (bypass LLM blind spots) ──
        forced_shift = self._detect_attitude_trigger(player_message, npc_def)
        if forced_shift is not None:
            parsed["attitude_shift"] = forced_shift

        # ── Killer guilt pressure: lying creates internal stress ──
        if npc_def.is_killer and topic_in_lie_range:
            existing = parsed.get("attitude_shift")
            if existing is None:
                parsed["attitude_shift"] = "-0.05，说谎时的内在压力"
            elif "-" in str(existing):
                # Amplify existing negative shift
                pass  # extraction already caught it

        # ── Update state (skip fabricated info) ──
        # Remember arc state before update for phase gating
        arc_before = npc_state.current_arc_state
        self.state_mgr.update_after_reply(npc_def, npc_state, player_id, parsed)

        # Phase gating: confession/max-reveal states only in ACT_4+
        if npc_state.current_arc_state != arc_before:
            if self._is_confession_state(npc_state) and not self._phase_allows_confession(phase):
                npc_state.current_arc_state = arc_before  # Roll back
                # Force evasion instead of confession
                parsed["info_revealed"] = [i for i in parsed.get("info_revealed", [])
                                           if i.get("level") != "L4"]

        return NPCReply(
            npc_id=npc_def.npc_id,
            npc_name=npc_def.name,
            reply_text=reply_text,
            emotional_tag=parsed.get("emotional_tag", npc_state.emotional_tag),
            info_revealed=parsed.get("info_revealed", []),
            attitude_shift=parsed.get("attitude_shift"),
            arc_state_transition=parsed.get("arc_state_transition"),
            dialogue_latency_ms=dialogue_resp.latency_ms,
            extraction_latency_ms=extraction_resp.latency_ms,
            tokens_used=dialogue_resp.tokens_used + extraction_resp.tokens_used,
            fabrication_detected=bool(corrected),
            original_reply=original,
        )

    # Keyword → stimulus type mapping (personality adjusts the actual delta)
    STIMULUS_KEYWORDS = [
        # (keywords, stimulus_type)
        (["凶手", "杀人", "你杀的", "你干的", "你是真凶", "你害死"], "accusation"),
        (["满口谎言", "满嘴谎言", "大骗子", "你一直在骗"], "insult"),
        (["撒谎", "说谎", "骗人", "骗子", "你编的", "胡扯", "矛盾", "站不住脚", "拆穿"], "suspicion"),
        (["混蛋", "贱", "不要脸", "滚", "去死", "恶心"], "insult"),
        (["相信你", "信任你", "我理解你", "你不是那种人", "我相信"], "trust"),
        (["热爱", "艺术家", "厉害", "很棒", "了不起", "佩服", "欣赏美", "懂美", "有品位", "才华"], "compliment"),
        (["谢谢", "感谢", "感激", "帮了大忙"], "gratitude"),
    ]

    def _detect_attitude_trigger(self, player_message: str, npc_def) -> str | None:
        """Personality-driven attitude reaction.

        Different NPCs react differently to the same player words.
        A fiery NPC (high aggression) swings hard on insults.
        A gentle NPC (low aggression) withdraws quietly.
        A rational NPC barely moves on provocation.
        """
        profile = npc_def.personality.attitude_profile()

        for keywords, stim_type in self.STIMULUS_KEYWORDS:
            for kw in keywords:
                if kw in player_message:
                    base, multiplier = profile[stim_type]
                    effective = base * multiplier
                    # Cumulative: consecutive same-direction hits amplify
                    same_dir = (effective < 0 and self._last_trigger_negative) or \
                               (effective > 0 and not self._last_trigger_negative)
                    if same_dir:
                        effective *= 1.3
                    self._last_trigger_negative = (effective < 0)
                    reason_map = {
                        "accusation": "被直接指控",
                        "insult": "受到辱骂",
                        "suspicion": "被质疑诚实",
                        "trust": "感受到信任",
                        "compliment": "受到赞美",
                        "gratitude": "收到感谢",
                    }
                    return f"{effective:+.2f}，{reason_map.get(stim_type, stim_type)}"
        self._last_trigger_negative = False
        return None

    # Confession arc state names (phase-gated: only in ACT_4+)
    CONFESSION_STATES = {"confession", "breakdown_honest"}

    @staticmethod
    def _is_confession_state(npc_state) -> bool:
        return npc_state.current_arc_state in NPCsEngine.CONFESSION_STATES

    @staticmethod
    def _phase_allows_confession(phase: GamePhase) -> bool:
        return phase in (GamePhase.ACT_4_VOTE, GamePhase.FINISHED)

    def _guard_fabrication(
        self,
        parsed: dict,
        reply_text: str,
        npc_def: NPCDefinition,
        npc_state: NPCState,
    ) -> tuple[str, str]:
        """Check extraction output for fabricated content.

        Returns (corrected_reply, original_reply).
        If no fabrication detected, returns ("", "").
        Killers are exempt — they are allowed to lie within their configured range.
        """
        if npc_def.is_killer:
            return "", ""

        inferred_items = [
            info for info in parsed.get("info_revealed", [])
            if info.get("inferred") is True
        ]
        fidelity_low_items = [
            info for info in parsed.get("info_revealed", [])
            if info.get("fidelity_low") is True
        ]

        if not inferred_items and not fidelity_low_items:
            return "", ""

        # Strip bad items from metadata
        parsed["info_revealed"] = [
            info for info in parsed.get("info_revealed", [])
            if not info.get("inferred") and not info.get("fidelity_low")
        ]

        # For non-killers: any fabrication triggers reply replacement
        # For killers on lie topics: only strip metadata, keep the lie reply
        if npc_def.is_killer and fidelity_low_items and not inferred_items:
            return "", ""  # Killer's imperfect lie — acceptable, just clean metadata

        # Pick evasion replacement
        strategy = npc_def.default_silence_strategy or SilenceStrategy.POLITE_REFUSAL
        templates = EVASION_TEMPLATES.get(strategy, EVASION_TEMPLATES[SilenceStrategy.POLITE_REFUSAL])

        # Deterministic pick based on message length to avoid randomness
        idx = len(reply_text) % len(templates)
        evasion = templates[idx]

        return evasion, reply_text
