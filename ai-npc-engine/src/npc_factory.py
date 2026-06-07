"""NPCFactory — personality-driven NPC templates with proven defaults.

Lessons baked in from extensive testing:
- Gentle non-killers need anti-fabrication enforcement + slow breakdown thresholds
- Hardened killers need high rationality, phase-gated confession, skillful deflection
- Timid bystanders need anxiety sensitivity, easy intimidation
- Fiery suspects need anger sensitivity, explosive but brief reactions
"""
from __future__ import annotations

from .models import (
    ArcState, ArcTransition, InfoLevel, NPCDefinition, PersonalityMatrix,
    Relationship, SelfAwareness, SilenceStrategy,
)


class NPCFactory:
    """Create NPC definitions with sensible defaults based on personality type."""

    @staticmethod
    def gentle_non_killer(
        npc_id: str, name: str, age: int, occupation: str,
        character_anchor: str, knowledge: list,
        relationships: list[Relationship] | None = None,
    ) -> NPCDefinition:
        """Gentle, cooperative, slow to anger. Default for most non-killer NPCs.

        Proven config from 苏晚晴 testing:
        - Low aggression (0.1) → gentle responses to insults
        - High rationality (0.7) → controlled emotions
        - Moderate honesty (0.8) → defaults to truth
        - Arc: distant → interested → defensive → breakdown
        - Recovery from defensive possible (needs +0.3 attitude)
        - Breakdown needs sadness-mid or higher
        """
        arc_states = [
            ArcState("distant_polite", "疏离客气",
                "温和礼貌但保持距离。回答简短，不主动展开。",
                0.0, [InfoLevel.L1], [SilenceStrategy.POLITE_REFUSAL], "平静"),
            ArcState("slightly_interested", "稍有兴趣",
                "语气多了温度。可以透露L2。会在回答后反问玩家。",
                0.2, [InfoLevel.L1, InfoLevel.L2], [SilenceStrategy.DEFLECT], "平静"),
            ArcState("defensive_tense", "防御紧绷",
                "明显紧张，回答谨慎。用沉默或转移回避敏感话题。",
                -0.3, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3],
                [SilenceStrategy.CHANGE_SUBJECT, SilenceStrategy.EMOTIONAL_AVOIDANCE],
                "紧张-低"),
            ArcState("breakdown_honest", "崩溃坦白",
                "防线崩溃。用轻而颤抖的声音说出真相。",
                0.5, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4],
                [], "悲伤-中"),
        ]
        arc_transitions = [
            # Forward
            ArcTransition("distant_polite", "slightly_interested", "attitude>=0.15"),
            ArcTransition("slightly_interested", "defensive_tense", "attitude<=-0.2"),
            ArcTransition("distant_polite", "defensive_tense", "attitude<=-0.3"),
            ArcTransition("distant_polite", "defensive_tense", "emotion_contains=紧张"),
            # Breakdown — needs trust+sadness, or very high trust
            ArcTransition("slightly_interested", "breakdown_honest",
                          "attitude>=0.5 AND emotion_contains=悲伤"),
            ArcTransition("slightly_interested", "breakdown_honest", "attitude>=0.7"),
            ArcTransition("defensive_tense", "breakdown_honest", "attitude>=0.4"),
            ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=悲伤-中"),
            ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=悲伤-高"),
            ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=哀恸"),
            # Recovery
            ArcTransition("defensive_tense", "slightly_interested", "attitude>=0.3"),
            ArcTransition("defensive_tense", "distant_polite", "attitude>=0.5"),
            ArcTransition("breakdown_honest", "slightly_interested", "attitude>=0.3"),
        ]
        return NPCDefinition(
            npc_id=npc_id, name=name, age=age, occupation=occupation,
            character_anchor=character_anchor,
            personality=PersonalityMatrix(
                extroversion=0.3, aggression=0.1, honesty_tendency=0.8,
                rationality=0.7, speech_style="温和克制，偶尔流露情绪",
            ),
            self_awareness=SelfAwareness.NEVER_KNOWS, is_killer=False,
            knowledge=knowledge,
            relationships=relationships or [],
            default_silence_strategy=SilenceStrategy.POLITE_REFUSAL,
            silence_triggers=[],
            arc_states=arc_states, arc_transitions=arc_transitions,
            initial_arc_state="distant_polite",
        )

    @staticmethod
    def hardened_killer(
        npc_id: str, name: str, age: int, occupation: str,
        character_anchor: str, knowledge: list, lie_topics: list,
        relationships: list[Relationship] | None = None,
    ) -> NPCDefinition:
        """Skilled liar, excellent self-control, will NOT crack before Act 4.

        Proven config from 周明远 testing:
        - High rationality (0.85) → emotions deeply suppressed
        - High extroversion (0.7) → skilled at deflection and counter-questioning
        - Low honesty (0.2) → lies fluidly
        - 5 arc states with granular progression
        - Confession requires attitude <= -0.70 or double-emotion combo
        - Confession is phase-gated at engine level (only in Act 4+)
        """
        arc_states = [
            ArcState("calm_composed", "从容自若",
                "谈笑风生，对答如流。主动反问，掌握节奏。",
                0.0, [InfoLevel.L1], [], "平静"),
            ArcState("evasive_controlled", "回避但受控",
                "依然从容。用圆滑措辞绕开敏感话题，像政治家答记者问。",
                0.0, [InfoLevel.L1, InfoLevel.L2], [SilenceStrategy.DEFLECT], "平静"),
            ArcState("guarded_tense", "暗流涌动",
                "表面得体，但细心能察觉握杯力度、语句微顿。开始反问转守为攻。",
                -0.15, [InfoLevel.L1, InfoLevel.L2],
                [SilenceStrategy.DEFLECT, SilenceStrategy.CHANGE_SUBJECT], "紧张-低"),
            ArcState("cornered_defensive", "角落反扑",
                "不再维持完美面具。话语锋利，用逻辑漏洞反击，转移焦点。",
                -0.3, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3],
                [SilenceStrategy.CHANGE_SUBJECT], "愤怒-低"),
            ArcState("confession", "面具碎裂",
                "漫长沉默后，用几乎听不见的声音说出真相。",
                -0.5, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4],
                [], "懊悔-高"),
        ]
        arc_transitions = [
            # Slow, resistant progression
            ArcTransition("calm_composed", "evasive_controlled", "attitude<=-0.15"),
            ArcTransition("calm_composed", "evasive_controlled",
                          "emotion_contains=紧张 AND attitude<=-0.05"),
            ArcTransition("evasive_controlled", "guarded_tense", "attitude<=-0.30"),
            ArcTransition("evasive_controlled", "guarded_tense", "emotion_contains=愤怒"),
            ArcTransition("evasive_controlled", "guarded_tense", "emotion_contains=恐惧"),
            ArcTransition("guarded_tense", "cornered_defensive", "attitude<=-0.45"),
            ArcTransition("guarded_tense", "cornered_defensive",
                          "attitude<=-0.30 AND emotion_contains=愤怒"),
            # Confession — requires overwhelming pressure (additionally phase-gated by engine)
            ArcTransition("cornered_defensive", "confession", "attitude<=-0.70"),
            ArcTransition("cornered_defensive", "confession",
                          "attitude<=-0.50 AND emotion_contains=懊悔 AND emotion_contains=悲伤"),
            ArcTransition("cornered_defensive", "confession",
                          "emotion_contains=哀恸 AND attitude<=-0.40"),
            # Recovery (regains composure easily)
            ArcTransition("evasive_controlled", "calm_composed", "attitude>=0.10"),
            ArcTransition("guarded_tense", "evasive_controlled", "attitude>=0.05"),
            ArcTransition("cornered_defensive", "guarded_tense", "attitude>=0.0"),
        ]
        return NPCDefinition(
            npc_id=npc_id, name=name, age=age, occupation=occupation,
            character_anchor=character_anchor,
            personality=PersonalityMatrix(
                extroversion=0.7, aggression=0.4, honesty_tendency=0.2,
                rationality=0.85, speech_style="从容不迫，善于反问和掌控对话节奏",
            ),
            self_awareness=SelfAwareness.KNOWS_IS_KILLER, is_killer=True,
            knowledge=knowledge,
            relationships=relationships or [],
            lie_topics=lie_topics,
            arc_states=arc_states, arc_transitions=arc_transitions,
            initial_arc_state="calm_composed",
        )

    @staticmethod
    def timid_bystander(
        npc_id: str, name: str, age: int, occupation: str,
        character_anchor: str, knowledge: list,
        relationships: list[Relationship] | None = None,
    ) -> NPCDefinition:
        """Easily intimidated, truthful but anxious. Cracks under minor pressure.

        - Low aggression (0.05) → submissive
        - Low extroversion (0.2) → anxious, avoids eye contact
        - High honesty (0.9) → blurts truth when nervous
        - Quick to enter defensive states
        - Low breakdown threshold
        """
        arc_states = [
            ArcState("nervous_polite", "拘谨礼貌",
                "说话轻声细语，不敢直视。回答简短。",
                0.0, [InfoLevel.L1], [SilenceStrategy.POLITE_REFUSAL], "紧张-低"),
            ArcState("anxious_open", "焦虑坦白",
                "紧张到语速变快。主动透露信息以求自保。",
                0.1, [InfoLevel.L1, InfoLevel.L2], [], "紧张-中"),
            ArcState("terrified_confession", "恐惧招供",
                "彻底吓坏了。把所有知道的事都说出来。",
                -0.1, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4],
                [], "恐惧-高"),
        ]
        arc_transitions = [
            ArcTransition("nervous_polite", "anxious_open", "emotion_contains=紧张"),
            ArcTransition("nervous_polite", "anxious_open", "attitude<=-0.10"),
            ArcTransition("anxious_open", "terrified_confession", "attitude<=-0.2"),
            ArcTransition("anxious_open", "terrified_confession", "emotion_contains=恐惧"),
            ArcTransition("terrified_confession", "anxious_open", "attitude>=0.15"),
        ]
        return NPCDefinition(
            npc_id=npc_id, name=name, age=age, occupation=occupation,
            character_anchor=character_anchor,
            personality=PersonalityMatrix(
                extroversion=0.2, aggression=0.05, honesty_tendency=0.9,
                rationality=0.4, speech_style="轻声细语，紧张时结巴，容易被吓到",
            ),
            self_awareness=SelfAwareness.NEVER_KNOWS, is_killer=False,
            knowledge=knowledge,
            relationships=relationships or [],
            default_silence_strategy=SilenceStrategy.POLITE_REFUSAL,
            silence_triggers=[],
            arc_states=arc_states, arc_transitions=arc_transitions,
            initial_arc_state="nervous_polite",
        )

    @staticmethod
    def fiery_suspect(
        npc_id: str, name: str, age: int, occupation: str,
        character_anchor: str, knowledge: list,
        relationships: list[Relationship] | None = None,
    ) -> NPCDefinition:
        """Hot-tempered, easily provoked. Explosive but recovers quickly.

        - High aggression (0.85) → big negative swings
        - Moderate extroversion (0.5) → expresses anger openly
        - Moderate rationality (0.3) → emotional, impulsive
        - Explosive transitions with fast recovery
        """
        arc_states = [
            ArcState("brusque_neutral", "粗鲁中立",
                "语气直接，不耐烦。但信息给得痛快。",
                0.0, [InfoLevel.L1], [], "平静"),
            ArcState("erupted_anger", "爆发愤怒",
                "拍桌子。大声反驳。但愤怒过后反而会透露更多。",
                -0.3, [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3],
                [], "愤怒-高"),
            ArcState("grudging_calm", "余怒未消",
                "怒气过去了，但还在不爽。话变少，但不再撒谎。",
                -0.1, [InfoLevel.L1, InfoLevel.L2],
                [SilenceStrategy.CHANGE_SUBJECT], "不满-低"),
        ]
        arc_transitions = [
            ArcTransition("brusque_neutral", "erupted_anger", "attitude<=-0.2"),
            ArcTransition("brusque_neutral", "erupted_anger", "emotion_contains=愤怒"),
            ArcTransition("erupted_anger", "grudging_calm", "attitude>=0.0"),
            ArcTransition("grudging_calm", "erupted_anger", "attitude<=-0.3"),
            ArcTransition("grudging_calm", "brusque_neutral", "attitude>=0.2"),
        ]
        return NPCDefinition(
            npc_id=npc_id, name=name, age=age, occupation=occupation,
            character_anchor=character_anchor,
            personality=PersonalityMatrix(
                extroversion=0.5, aggression=0.85, honesty_tendency=0.6,
                rationality=0.3, speech_style="直来直去，嗓门大，藏不住话也藏不住脾气",
            ),
            self_awareness=SelfAwareness.NEVER_KNOWS, is_killer=False,
            knowledge=knowledge,
            relationships=relationships or [],
            default_silence_strategy=SilenceStrategy.CHANGE_SUBJECT,
            silence_triggers=[],
            arc_states=arc_states, arc_transitions=arc_transitions,
            initial_arc_state="brusque_neutral",
        )
