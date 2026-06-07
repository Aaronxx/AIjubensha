"""ScriptValidator — checks NPC definitions against proven rules.

All rules below come from issues found and fixed during testing.
Run this before deploying a new script to catch common problems early.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    ArcTransition, InfoLevel, KnowledgeEntry, NPCDefinition,
)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


class ScriptValidator:
    """Validates NPC definitions against framework rules."""

    def validate(self, npc_def: NPCDefinition) -> ValidationResult:
        result = ValidationResult()
        self._check_knowledge_metadata(npc_def, result)
        self._check_arc_reachability(npc_def, result)
        self._check_confession_gating(npc_def, result)
        self._check_lie_topic_completeness(npc_def, result)
        self._check_personality_consistency(npc_def, result)
        self._check_breakdown_threshold(npc_def, result)
        return result

    def _check_knowledge_metadata(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: All L2+ knowledge entries should have time/location labels."""
        for k in npc.knowledge:
            if k.level in (InfoLevel.L2, InfoLevel.L3, InfoLevel.L4):
                if not k.time_label and not k.location_label:
                    r.warnings.append(
                        f"{npc.name}: '{k.content[:30]}...' ({k.level.value}) "
                        f"缺少时间/地点标签 —— NPC可能混淆不同事件的事实"
                    )

    def _check_arc_reachability(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: Every non-initial arc state should be reachable from the initial state."""
        if not npc.arc_states or not npc.arc_transitions:
            return

        state_names = {s.name for s in npc.arc_states}
        initial = npc.initial_arc_state or npc.arc_states[0].name

        # BFS from initial state
        reachable = {initial}
        changed = True
        while changed:
            changed = False
            for t in npc.arc_transitions:
                if t.from_state in reachable and t.to_state not in reachable:
                    reachable.add(t.to_state)
                    changed = True

        unreachable = state_names - reachable
        if unreachable:
            r.errors.append(
                f"{npc.name}: 以下弧状态从初始状态'{initial}'不可达: {unreachable}"
            )

    def _check_confession_gating(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: Confession/max-reveal states should have high thresholds.

        'confession' or 'breakdown_honest' states should require:
        - attitude <= -0.50 (hardened killer) or attitude >= 0.40 (gentle NPC)
        - Plus an emotion condition for extra safety
        """
        confession_states = {"confession", "breakdown_honest", "terrified_confession"}
        for t in npc.arc_transitions:
            if t.to_state in confession_states:
                condition = t.trigger_condition
                # Check if condition has adequate safeguards
                has_emotion = "emotion_contains" in condition
                has_attitude = "attitude" in condition

                if not has_emotion and "attitude>=0.5" not in condition:
                    r.warnings.append(
                        f"{npc.name}: 进入'{t.to_state}'的条件'{condition}' "
                        f"缺少情绪条件——可能'轻易崩溃'"
                    )

    def _check_lie_topic_completeness(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: Killer NPCs should have lie topics covering their key secrets."""
        if not npc.is_killer:
            return
        if not npc.lie_topics:
            r.warnings.append(
                f"{npc.name}: 是凶手但没有配置谎言辐射范围——"
                f"可能在所有话题都说真话"
            )

    def _check_personality_consistency(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: Personality should match arc state design."""
        p = npc.personality

        # Hardened killer check: high rationality + high extroversion are expected
        if npc.is_killer:
            if p.rationality < 0.6:
                r.warnings.append(
                    f"{npc.name}: 凶手NPC理性值偏低({p.rationality})——"
                    f"建议>=0.6以便伪装真实情绪"
                )
            if p.extroversion < 0.5:
                r.warnings.append(
                    f"{npc.name}: 凶手NPC外向值偏低({p.extroversion})——"
                    f"建议>=0.5以便掌控对话节奏"
                )

    def _check_breakdown_threshold(self, npc: NPCDefinition, r: ValidationResult):
        """Rule: 'breakdown' transitions should not trigger on mild emotions.

        Using 'emotion_contains=悲伤' catches '悲伤-低' which is too easy.
        Should specify '悲伤-中' or '悲伤-高' for breakdown triggers.
        """
        for t in npc.arc_transitions:
            if "breakdown" in t.to_state or "confession" in t.to_state:
                if "emotion_contains=" in t.trigger_condition:
                    tag = t.trigger_condition.split("emotion_contains=")[-1].strip()
                    # Split AND combos
                    tags_to_check = [tag.split(" AND ")[0].strip()]
                    for check_tag in tags_to_check:
                        if check_tag in ("悲伤", "懊悔") and "-" not in check_tag:
                            r.warnings.append(
                                f"{npc.name}: 进入'{t.to_state}'的条件使用了"
                                f"'{check_tag}'而非'{check_tag}-中'——"
                                f"任何等级的{check_tag}都会触发，门槛太低"
                            )
