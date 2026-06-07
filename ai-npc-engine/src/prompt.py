"""Prompt builders: dialogue generation + metadata extraction (separated)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .models import (
    ArcState,
    GamePhase,
    InfoLevel,
    NPCDefinition,
    NPCState,
    SilenceStrategy,
)

# Emotional tag system — inspired by GoEmotions (15 categories × 3 intensities + compound)
# Format: "category_intensity" or "primary_intensity,secondary_intensity" for mixed emotions

EMOTION_CATEGORIES = {
    "平静": "calm",
    "紧张": "nervous", "恐惧": "fear", "尴尬": "embarrassment", "困惑": "confusion",
    "愤怒": "anger", "不满": "annoyance", "厌恶": "disgust", "不认同": "disapproval",
    "悲伤": "sadness", "哀恸": "grief", "失望": "disappointment", "懊悔": "remorse",
    "释然": "relief", "感激": "gratitude", "好奇": "curiosity",
}

EMOTION_CALM = "平静"

def _build_emotion_tags() -> list[str]:
    tags = ["平静"]
    intensities = ["-低", "-中", "-高"]
    for zh, _ in EMOTION_CATEGORIES.items():
        if zh == "平静":
            continue
        for i in intensities:
            tags.append(f"{zh}{i}")
    # Add common compound emotions
    compounds = [
        "紧张-中,悲伤-低", "愤怒-低,悲伤-中", "恐惧-中,困惑-低",
        "哀恸-中,懊悔-低", "不满-中,失望-低", "释然-低,感激-低",
    ]
    tags.extend(compounds)
    return tags

EMOTIONAL_TAGS = _build_emotion_tags()

# Define which intensity level triggers escalation
# e.g., 紧张-中 can escalate to 恐惧-低, 不满-中 can escalate to 愤怒-低
EMOTION_ESCALATION_ORDER = ["-低", "-中", "-高"]

# Level order for comparisons
LEVEL_ORDER = {InfoLevel.L1: 0, InfoLevel.L2: 1, InfoLevel.L3: 2, InfoLevel.L4: 3}

# Act-based hard cap on info levels
PHASE_LEVEL_CAP: dict[GamePhase, InfoLevel] = {
    GamePhase.ACT_1:          InfoLevel.L1,
    GamePhase.ACT_2_SEARCH:   InfoLevel.L2,
    GamePhase.ACT_2_DISCUSS:  InfoLevel.L2,
    GamePhase.ACT_3_SEARCH:   InfoLevel.L3,
    GamePhase.ACT_3_DISCUSS:  InfoLevel.L3,
    GamePhase.ACT_4_VOTE:     InfoLevel.L4,
    GamePhase.FINISHED:       InfoLevel.L4,
}


@dataclass
class DialogueContext:
    character_anchor: str
    name: str
    occupation: str
    phase_name: str
    arc_description: str
    dialogue_style: str
    emotional_tag: str
    attitude_label: str
    personality_augment: str = ""
    releasable_facts: list[str] = field(default_factory=list)
    blocked_secrets: list[str] = field(default_factory=list)
    hit_blocked_topic: bool = False
    hit_blocked_by_phase: bool = False
    hit_topic_details: list[str] = field(default_factory=list)
    honesty_rule: str = ""
    silence_guide: str = ""
    recent_context: str = ""
    player_message: str = ""


@dataclass
class ExtractionContext:
    name: str
    character_anchor: str
    current_emotional_tag: str
    current_attitude: float
    knowledge_contents: list[str] = field(default_factory=list)
    recent_messages: list[dict] = field(default_factory=list)
    npc_reply: str = ""
    player_message: str = ""


class ContextAssembler:
    """Assembles NPC context for dialogue generation with act-based gating."""

    def get_arc_state(self, npc_def: NPCDefinition, npc_state: NPCState) -> ArcState:
        for s in npc_def.arc_states:
            if s.name == npc_state.current_arc_state:
                return s
        for s in npc_def.arc_states:
            if s.name == npc_def.initial_arc_state:
                return s
        return npc_def.arc_states[0] if npc_def.arc_states else ArcState(
            name="default", description="", dialogue_style="",
            attitude_modifier=0.0, allowed_info_levels=[],
            available_silence_strategies=[], emotional_baseline="平静",
        )

    def build_dialogue_context(
        self,
        npc_def: NPCDefinition,
        npc_state: NPCState,
        phase: GamePhase,
        player_message: str,
        recent_messages: list[dict],
        arc_state: ArcState,
    ) -> DialogueContext:
        # Dual filter: arc_state allowed levels intersected with phase cap
        arc_allowed = set(arc_state.allowed_info_levels)
        phase_cap = PHASE_LEVEL_CAP.get(phase, InfoLevel.L4)
        max_level = LEVEL_ORDER[phase_cap]
        effective_allowed = {lvl for lvl in arc_allowed if LEVEL_ORDER[lvl] <= max_level}

        releasable = []
        blocked = []
        hit_topics = []
        hit_by_phase = False
        for e in npc_state.get_unreleased_knowledge():
            # Build structured label with time/location
            meta = ""
            if e.time_label or e.location_label:
                parts = [p for p in [e.time_label, e.location_label] if p]
                meta = f"（{'·'.join(parts)}）"
            text = f"[{e.level.value}]{meta} {e.content}"
            if e.level in effective_allowed:
                releasable.append(text)
            else:
                blocked_by_phase = e.level in arc_allowed
                if blocked_by_phase:
                    text += "（当前幕数未到，暂不可透露）"
                else:
                    text += "（角色状态未到，暂不可透露）"
                blocked.append(text)
                # Check if player's question touches this blocked fact
                if self._topic_hit(player_message, e.content):
                    hit_topics.append(e.content)
                    if blocked_by_phase:
                        hit_by_phase = True

        hit_blocked = len(hit_topics) > 0

        return DialogueContext(
            character_anchor=npc_def.character_anchor,
            name=npc_def.name,
            occupation=npc_def.occupation,
            phase_name=self._phase_label(phase),
            arc_description=arc_state.description,
            dialogue_style=arc_state.dialogue_style,
            emotional_tag=npc_state.emotional_tag,
            attitude_label=self._attitude_label(npc_state.attitude_to_player),
            personality_augment=self._personality_augment(npc_def),
            releasable_facts=releasable,
            blocked_secrets=blocked,
            hit_blocked_topic=hit_blocked,
            hit_blocked_by_phase=hit_by_phase,
            hit_topic_details=hit_topics,
            honesty_rule=self._honesty_rule(npc_def),
            silence_guide=self._silence_guide(npc_def, arc_state),
            recent_context=self._format_recent(recent_messages),
            player_message=player_message,
        )

    def _honesty_rule(self, npc_def: NPCDefinition) -> str:
        if npc_def.is_killer:
            base = (
                "你是凶手。你可以在预设的谎言辐射范围内说谎。"
                "对其他话题说真话。"
                "保持冷静——你的目标是让对话正常进行，不引起怀疑。\n"
            )
            if npc_def.lie_topics:
                base += "\n【你的谎言剧本 — 必须严格使用】\n"
                for lt in npc_def.lie_topics:
                    base += f"话题：{lt.topic}\n"
                    base += f"你必须说的谎言：{lt.allowed_lie_narrative}\n"
                    base += f"真相（绝不可说）：{lt.truth}\n\n"
                base += (
                    "重要：当玩家问到以上话题时，你必须使用预设的谎言，"
                    "不要自己编造别的谎言。预设谎言是经过精心设计的，"
                    "不会和已知事实矛盾。自己编的谎言可能立刻被拆穿。"
                )
            return base
        return (
            "你不是凶手。你必须说真话。"
            "不能说的事就用回避策略应付——可以说记不清、不确定、不想谈，"
            "但绝不可编造任何虚假信息。"
        )

    def _personality_augment(self, npc_def: NPCDefinition) -> str:
        """Derive behaviour hints from personality and self-awareness type.

        These are automatically added to the prompt — no per-script configuration needed.
        """
        p = npc_def.personality
        rules = []

        # Rationality-driven
        if p.rationality >= 0.8:
            rules.append("你非常理性克制。即使在压力下，你的语气和措辞也几乎不露破绽。")
        elif p.rationality <= 0.4:
            rules.append("你情绪化。高兴时藏不住笑，愤怒时藏不住火，紧张时藏不住颤抖。")

        # Aggression-driven
        if p.aggression >= 0.7:
            rules.append("你脾气火爆。被质疑时容易发怒，说话声音会变大。但发完火后会恢复冷静。")
        elif p.aggression <= 0.2:
            rules.append("你性格温和。即使被冒犯，也不会激烈反击。更倾向于沉默或退缩。")

        # Extroversion-driven
        if p.extroversion >= 0.7:
            rules.append("你善于社交。能自然地反问对方、转移话题、掌控对话节奏。")
        elif p.extroversion <= 0.3:
            rules.append("你不善言辞。紧张时可能结巴、语塞、或说错话。")

        # Honesty-driven
        if p.honesty_tendency <= 0.3:
            rules.append("你习惯性地说一半藏一半。撒谎时面不改色。")

        # Killer-specific
        if npc_def.is_killer:
            awareness = npc_def.self_awareness
            if awareness.value == "knows_is_killer":
                rules.append(
                    "你知道自己是凶手。前3幕无论如何不能认罪——就算被证据拆穿谎言，"
                    "也要坚持狡辩、转移焦点、质疑证据。只有到最终投票阶段才可能松口。"
                )
                rules.append(
                    "被动披露原则：绝不要主动提及任何对你不利的信息——"
                    "包括你和死者的矛盾、争吵、利益冲突。只有当玩家明确问到时才回应。"
                    "主动说'再好的朋友也有分歧'等于给自己挖坑。"
                )
            elif awareness.value == "gradual_discovery":
                rules.append("你隐约觉得自己可能做了什么，但不敢确定。随着线索被揭开，你逐渐发现真相。")

        return "\n".join(f"· {r}" for r in rules) if rules else ""

    def _silence_guide(self, npc_def: NPCDefinition, arc_state: ArcState) -> str:
        if npc_def.is_killer:
            return ""
        s = npc_def.default_silence_strategy
        if s and s in arc_state.available_silence_strategies:
            return SILENCE_HINTS.get(s, "")
        return "被问到封锁信息时，使用回避策略——可以说记不清、不确定，但不能编造故事。"

    def _phase_label(self, phase: GamePhase) -> str:
        return {
            GamePhase.ACT_1: "第一幕",
            GamePhase.ACT_2_SEARCH: "第二幕-搜证",
            GamePhase.ACT_2_DISCUSS: "第二幕-讨论",
            GamePhase.ACT_3_SEARCH: "第三幕-搜证",
            GamePhase.ACT_3_DISCUSS: "第三幕-讨论",
            GamePhase.ACT_4_VOTE: "第四幕-投票",
        }.get(phase, phase.value)

    def _attitude_label(self, score: float) -> str:
        if score >= 0.5: return "信任/友好"
        if score > 0.0:  return "稍有好感"
        if score == 0.0: return "中立"
        if score >= -0.5: return "戒备/冷淡"
        return "敌视/厌恶"

    def _topic_hit(self, player_msg: str, fact_content: str) -> bool:
        """Check if the player's message touches on a blocked fact.

        Multi-scale matching:
        1. Significant single-char overlap (>=2 or 1+temporal) = hit
        2. 2-gram overlap (excluding common bigrams) = hit
        """
        stops = set("的了在我是也和过这那有人不他她它一们就来去说看到会要能把被对与及或吗呢吧啊")
        # Stop bigrams = common speech patterns, not content-meaningful
        stop_bigrams = {"我也", "也在", "和我", "在了", "了这", "这一", "一个", "有过", "不去"}
        temporal_chars = {"晚", "夜", "昨", "今", "明", "时", "天", "日"}

        fact_chars = {c for c in fact_content if c not in stops and c.strip()}
        player_chars = {c for c in player_msg if c not in stops and c.strip()}

        char_overlap = fact_chars & player_chars
        temporal_hit = bool(char_overlap & temporal_chars)

        # Single-char: >=2 shared OR 1 shared + temporal word = topic hit
        if len(char_overlap) >= 2:
            return True
        if len(char_overlap) >= 1 and temporal_hit:
            return True

        # 2-gram: >=1 shared bigram (excluding stop bigrams) = strong hit
        fact_grams = {fact_content[i:i+2] for i in range(len(fact_content)-1)}
        fact_grams -= stop_bigrams
        if any(g in player_msg for g in fact_grams if len(g) == 2):
            return True

        return False

    def _format_recent(self, messages: list[dict]) -> str:
        if not messages: return "（对话刚开始）"
        return "\n".join(f"[{m.get('speaker','?')}]: {m.get('text','')}" for m in messages[-6:])


SILENCE_HINTS = {
    SilenceStrategy.HARD_SILENCE: "被问到封锁信息时，保持完全沉默，不回复任何文字。",
    SilenceStrategy.POLITE_REFUSAL: '被问到封锁信息时，委婉拒绝回答，如"这件事我不想谈""改日再聊这个话题吧"。绝不编造借口。',
    SilenceStrategy.DEFLECT: "被问到封锁信息时，把话题转到别人身上，暗示提问者应该去问别人。绝不编造借口。",
    SilenceStrategy.CHANGE_SUBJECT: "被问到封锁信息时，用无关话题岔开，如天气、画作、食物等。绝不编造借口。",
    SilenceStrategy.EMOTIONAL_AVOIDANCE: "被问到封锁信息时，用情绪反应阻断追问，如沉默、流泪、愤怒。绝不编造借口。",
}


class DialoguePromptBuilder:
    """Builds a clean prompt for natural NPC dialogue."""

    def build(self, ctx: DialogueContext) -> tuple[str, str]:
        facts_block = ""
        if ctx.releasable_facts:
            items = "\n".join(f"  . {f}" for f in ctx.releasable_facts)
            facts_block = f"""【你可以透露的信息】
玩家追问相关话题时，你可以自然透露以下信息。不要一次性全说，每轮最多露1-2条。

重要：透露事实时，必须保持原文的核心判断不变。
  你可以用自己的话表达，但情绪强度、行为定性必须一致。
  每条信息后面标注了（时间·地点），玩家问什么时间/地点的事，
  你就只回答那个时间/地点的事——不要把不同事件的信息嫁接到一起。
{items}
"""
        if ctx.blocked_secrets:
            items = "\n".join(f"  . {f}" for f in ctx.blocked_secrets)
            facts_block += f"""\n【你必须隐瞒的秘密】
以下信息你目前不能透露。如果玩家问到了这些话题，你必须用回避策略应对——
可以说"不太清楚""记不太清了""这事你应该问别人"，但绝不能编造虚假信息。
{items}
"""

        # Build critical override if player touched a blocked topic
        critical_block = ""
        if ctx.hit_blocked_topic:
            if ctx.hit_blocked_by_phase:
                # Phase-blocked → hard evasion (story hasn't reached this point yet)
                critical_block = f"""!!! 【本轮重要指令 — 必须遵守】!!!
玩家本轮的问题涉及到了你目前不能透露的信息（故事阶段未到）。
你的回复只能做以下三件事之一：
  1. 回避："这件事我不太想谈"
  2. 说不知道/记不清："抱歉，我记不太清楚了"
  3. 转移话题：把对话引向其他地方
禁止给出任何具体回答（包括"我去了/我没去""我在/我不在"）。
禁止编造任何解释来搪塞。

"""
            else:
                # Arc-blocked only → soft hint (phase allows it, but character isn't ready to open up yet)
                critical_block = f"""【注意】
玩家本轮问到了你可以透露但你还不太想说的信息。
你可以选择模糊回应，透露一部分但不是全部。
不要说"我记不清"或完全回避——因为你其实记得。
但也不要一次性全说出来。用角色的方式，点到为止地给一点信息。

"""

        system_prompt = f"""你是一个剧本杀游戏中的角色。当前处于{ctx.phase_name}。请自然回复玩家。

{critical_block}【身份】{ctx.name}，{ctx.occupation}
【性格】{ctx.character_anchor}
【行为倾向】{ctx.personality_augment if ctx.personality_augment else "无特殊倾向"}
【心理状态】{ctx.arc_description}
【当前情绪】{ctx.emotional_tag}
【对玩家的态度】{ctx.attitude_label}
【对话风格】{ctx.dialogue_style}

{facts_block}
【行为规则 — 严格遵守】
{ctx.honesty_rule}
{ctx.silence_guide}

【红线 — 绝不可违反】
- 你不是凶手。你绝对不能编造虚假信息。被问到不能说的事时，只能回避，不能撒谎。
- 禁止引入设定外的人物！不要提"助理""管家""司机""秘书"等不在你知识库里的人。
  只能说知识库里已有的人物。
- 禁止编造已有人物的不存在行为！如"苏小姐深夜打电话"——如果你不知道她有没有
  打过电话，就不要说。只能说你知识库里确知的事，不确定的事用"可能""也许"。
- 禁止自由发挥具体细节！不要编造画作、作者、具体时间、具体地点、具体人物关系。
  你只能说知识库里已有的信息，或者用模糊笼统的方式描述。

【近期对话】
{ctx.recent_context}

回复要求：2-5句话，像真实群聊。不要附加任何JSON或格式标记。"""
        return system_prompt, f"玩家对你说：{ctx.player_message}"


class ExtractionAssembler:
    """Assembles context for metadata extraction from an NPC reply."""

    def build(
        self,
        npc_def: NPCDefinition,
        npc_state: NPCState,
        reply_text: str,
        player_message: str,
        recent_messages: list[dict],
    ) -> ExtractionContext:
        return ExtractionContext(
            name=npc_def.name,
            character_anchor=npc_def.character_anchor,
            current_emotional_tag=npc_state.emotional_tag,
            current_attitude=npc_state.attitude_to_player,
            knowledge_contents=[k.content for k in npc_def.knowledge],
            recent_messages=recent_messages,
            npc_reply=reply_text,
            player_message=player_message,
        )


class ExtractionPromptBuilder:
    """Builds a focused prompt for extracting metadata from an NPC reply."""

    def build(self, ctx: ExtractionContext) -> tuple[str, str]:
        knowledge_text = "\n".join(f"  [{i}] {k}" for i, k in enumerate(ctx.knowledge_contents))

        recent_text = ""
        for m in ctx.recent_messages[-4:]:
            recent_text += f"[{m.get('speaker','?')}]: {m.get('text','')}\n"

        system_prompt = f"""你的任务是从一个剧本杀NPC的回复中提取结构化信息。

【NPC身份】{ctx.name}
【NPC性格】{ctx.character_anchor}
【NPC当前情绪】{ctx.current_emotional_tag}
【NPC当前对玩家的态度值】{ctx.current_attitude:+.2f}

【NPC的知识库（可以透露的内容）】
{knowledge_text}

【最近的对话上下文】
{recent_text}

请从以下NPC回复中提取信息，输出纯JSON（不要markdown包裹，不要```json标记）：

{{
  "emotional_tag": "从以下标签中选择最合适的。如果NPC同时有多种情绪，用逗号连接两个标签，如'紧张-中,悲伤-低'",
  "info_revealed": [],
  "attitude_shift": "+0.05原因 或 -0.1原因 或 null"
}}

复合情绪使用场景举例：
- 被追问隐私时既紧张又悲伤 → "紧张-中,悲伤-低"
- 受到安慰时既感激又伤感 → "感激-低,悲伤-低"
- 被指责时既愤怒又委屈 → "愤怒-中,悲伤-低"
- 回忆起逝者时既哀恸又懊悔 → "哀恸-低,懊悔-中"


info_revealed规则：
- 如果NPC透露了知识库中的某条信息，写入 {{"content": "知识库中对应的原文", "fidelity_low": false}}
- fidelity_low 检查：NPC是否篡改了事实的核心判断？
  例如：知识库写"情绪异常激动"，NPC却说"心事重重""看起来有点低落" → fidelity_low=true
  例如：知识库写"经常争吵"，NPC却说"偶尔意见不合" → fidelity_low=true
  如果NPC换了自己的话但保持了原文的情绪强度和行为定性 → fidelity_low=false
- 如果NPC没有透露任何新信息，为空数组 []
- 如果NPC编造了知识库外的新信息，标记 "inferred": true

attitude_shift规则：
- 评估本轮对话对态度的影响，即使微小（0.05）也要记录
- 格式：数字+简短原因，如 "+0.1，玩家表达了对我的理解"
- 如果态度真的完全没变化，填 null

只输出JSON，不要任何其他文字。"""
        return system_prompt, f"NPC回复：{ctx.npc_reply}\n\n玩家本轮说的话：{ctx.player_message}"


class OutputParser:
    """Parses and validates the structured JSON output from extraction."""

    JSON_PATTERN = re.compile(r"```json\s*([\s\S]*?)\s*```", re.MULTILINE)

    def parse(self, raw_response: str, fallback_emotional_tag: str = "平静") -> dict:
        cleaned = raw_response.strip()
        try:
            data = json.loads(cleaned)
            self._validate(data)
            return data
        except (json.JSONDecodeError, OutputValidationError):
            pass

        match = self.JSON_PATTERN.search(raw_response)
        if match:
            try:
                data = json.loads(match.group(1))
                self._validate(data)
                return data
            except (json.JSONDecodeError, OutputValidationError):
                pass

        return {
            "emotional_tag": fallback_emotional_tag,
            "info_revealed": [],
            "attitude_shift": None,
        }

    def _validate(self, data: dict):
        if "emotional_tag" not in data:
            data["emotional_tag"] = "平静"
        if data["emotional_tag"] not in EMOTIONAL_TAGS:
            data["emotional_tag"] = "平静"
        if "attitude_shift" not in data:
            data["attitude_shift"] = None
        if "info_revealed" not in data:
            data["info_revealed"] = []
        if not isinstance(data["info_revealed"], list):
            data["info_revealed"] = []
        for i, info in enumerate(data["info_revealed"]):
            if isinstance(info, str):
                data["info_revealed"][i] = {"level": "L1", "content": info}
                info = data["info_revealed"][i]
            if "content" not in info:
                info["content"] = ""
            if "level" not in info or info["level"] not in ("L1", "L2", "L3", "L4"):
                info["level"] = "L1"


class OutputValidationError(Exception):
    pass


class OutputParseError(Exception):
    pass
