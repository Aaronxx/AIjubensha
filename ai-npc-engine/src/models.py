"""NPC state and game data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GamePhase(Enum):
    ACT_1 = "act_1"
    ACT_2_SEARCH = "act_2_search"
    ACT_2_DISCUSS = "act_2_discuss"
    ACT_3_SEARCH = "act_3_search"
    ACT_3_DISCUSS = "act_3_discuss"
    ACT_4_VOTE = "act_4_vote"
    FINISHED = "finished"


class InfoLevel(Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class SelfAwareness(Enum):
    KNOWS_IS_KILLER = "knows_is_killer"
    GRADUAL_DISCOVERY = "gradual_discovery"
    NEVER_KNOWS = "never_knows"
    CO_CONSPIRATOR = "co_conspirator"
    SCAPEGOAT = "scapegoat"


class SilenceStrategy(Enum):
    HARD_SILENCE = "hard_silence"
    POLITE_REFUSAL = "polite_refusal"
    DEFLECT = "deflect"
    CHANGE_SUBJECT = "change_subject"
    EMOTIONAL_AVOIDANCE = "emotional_avoidance"


class RelationType(Enum):
    COUPLE = "couple"
    COMRADE = "comrade"
    ENEMY = "enemy"
    NEUTRAL = "neutral"


RELATION_COVER_MAP = {
    RelationType.COUPLE: True,
    RelationType.COMRADE: True,
    RelationType.ENEMY: False,
    RelationType.NEUTRAL: False,
}


class EmotionCategory(Enum):
    """15 fine-grained emotions, grouped into 4 clusters + neutral baseline.
    Inspired by GoEmotions taxonomy, pruned for murder mystery context."""
    # Neutral
    CALM = "calm"

    # Anxiety cluster
    NERVOUS = "nervous"
    FEAR = "fear"
    EMBARRASSMENT = "embarrassment"
    CONFUSION = "confusion"

    # Anger cluster
    ANGER = "anger"
    ANNOYANCE = "annoyance"
    DISGUST = "disgust"
    DISAPPROVAL = "disapproval"

    # Sadness cluster
    SADNESS = "sadness"
    GRIEF = "grief"
    DISAPPOINTMENT = "disappointment"
    REMORSE = "remorse"

    # Positive cluster
    RELIEF = "relief"
    GRATITUDE = "gratitude"
    CURIOSITY = "curiosity"


# Emotion clusters for personality-driven sensitivity
EMOTION_CLUSTERS = {
    "anxiety": {EmotionCategory.NERVOUS, EmotionCategory.FEAR,
                EmotionCategory.EMBARRASSMENT, EmotionCategory.CONFUSION},
    "anger": {EmotionCategory.ANGER, EmotionCategory.ANNOYANCE,
              EmotionCategory.DISGUST, EmotionCategory.DISAPPROVAL},
    "sadness": {EmotionCategory.SADNESS, EmotionCategory.GRIEF,
                EmotionCategory.DISAPPOINTMENT, EmotionCategory.REMORSE},
    "positive": {EmotionCategory.RELIEF, EmotionCategory.GRATITUDE,
                 EmotionCategory.CURIOSITY},
}

# Cluster → cluster for natural emotional progression
# e.g., annoyance → anger → disgust; nervous → fear; sadness → grief
EMOTION_PROGRESSION: dict[EmotionCategory, EmotionCategory | None] = {
    EmotionCategory.NERVOUS: EmotionCategory.FEAR,
    EmotionCategory.CONFUSION: EmotionCategory.NERVOUS,
    EmotionCategory.ANNOYANCE: EmotionCategory.ANGER,
    EmotionCategory.ANGER: EmotionCategory.DISGUST,
    EmotionCategory.DISAPPROVAL: EmotionCategory.ANGER,
    EmotionCategory.SADNESS: EmotionCategory.GRIEF,
    EmotionCategory.DISAPPOINTMENT: EmotionCategory.SADNESS,
    EmotionCategory.EMBARRASSMENT: EmotionCategory.NERVOUS,
    EmotionCategory.GRIEF: None,  # Terminal
    EmotionCategory.FEAR: None,   # Terminal
    EmotionCategory.DISGUST: None,  # Terminal
    EmotionCategory.REMORSE: None,  # Terminal
    EmotionCategory.RELIEF: EmotionCategory.CALM,
    EmotionCategory.GRATITUDE: EmotionCategory.CALM,
    EmotionCategory.CURIOSITY: None,
    EmotionCategory.CALM: None,
}


@dataclass
class PersonalityMatrix:
    extroversion: float  # 0=introvert, 1=extrovert
    aggression: float  # 0=cooperative, 1=aggressive
    honesty_tendency: float  # 0=dishonest, 1=honest
    rationality: float  # 0=emotional, 1=rational
    speech_style: str  # description of speaking style

    def emotional_sensitivity(self) -> dict:
        """Which emotion clusters this NPC is prone to, and intensity multiplier.

        Returns dict[cluster_name, multiplier].
        multiplier > 1: NPC is more sensitive to this cluster.
        multiplier < 1: NPC is resistant to this cluster.
        """
        agg = self.aggression
        ext = self.extroversion
        rat = self.rationality  # dampens all emotional intensity

        # Base dampen: rational people feel less
        dampen = 1.0 - rat * 0.5

        return {
            "anger": (0.3 + agg * 1.7) * dampen,     # 0.3(cooperative) ~ 2.0(fiery)
            "anxiety": (1.5 - agg * 0.5) * dampen,    # 1.5(gentle) ~ 1.0(fiery)
            "sadness": (1.5 - agg * 0.3) * dampen,    # 1.5(gentle) ~ 1.2(fiery)
            "positive": (0.5 + ext * 1.0) * dampen,   # 0.5(introvert) ~ 1.5(extrovert)
        }

    def attitude_profile(self) -> dict:
        """Derive attitude reaction multipliers from personality.

        Returns a dict mapping stimulus types to (base_delta, multiplier).
        - base_delta: baseline attitude change for this stimulus
        - multiplier: personality-adjusted amplification

        Aggression amplifies negative reactions.
        Rationality dampens all reactions.
        Extroversion affects whether NPC uses avoidance vs direct response.
        """
        # Aggression: 0=gentle, 1=fiery
        # High aggression → big negative swings, small positive trust gain
        # Low aggression → mild negative swings, normal positive trust gain
        agg = self.aggression
        rat = self.rationality  # dampens emotional swings

        # aggress_mult: 0.5(gentle) ~ 2.0(fiery)
        aggress_mult = 0.5 + agg * 1.5
        # dampen: 0.4(rational) ~ 1.0(emotional)
        dampen = 1.0 - rat * 0.6

        return {
            "accusation":  (-0.15, aggress_mult * dampen),   # 指控
            "insult":      (-0.25, aggress_mult * dampen),   # 辱骂
            "trust":       (+0.10, dampen / max(aggress_mult, 0.5)),  # 信任
            "compliment":  (+0.08, dampen / max(aggress_mult, 0.5)),  # 赞美
            "gratitude":   (+0.05, dampen),                  # 感谢
            "suspicion":   (-0.10, aggress_mult * dampen),   # 质疑诚实
        }


@dataclass
class KnowledgeEntry:
    fact_id: str
    level: InfoLevel
    content: str
    release_condition: str  # e.g., "asked_directly", "trust>=0.5", "evidence_clue_05"
    time_label: str = ""    # e.g., "案发当晚", "上周四", "三年前"
    location_label: str = ""  # e.g., "山庄", "画廊", "晚宴"
    released: bool = False
    released_to: list[str] = field(default_factory=list)


@dataclass
class Relationship:
    target_id: str
    relation_type: RelationType
    will_cover_for: bool = False
    will_lie_for: bool = False
    will_take_blame_for: bool = False


@dataclass
class LieTopic:
    topic: str
    description: str
    truth: str
    allowed_lie_narrative: str


@dataclass
class ArcState:
    name: str
    description: str
    dialogue_style: str
    attitude_modifier: float  # -1.0 to 1.0
    allowed_info_levels: list[InfoLevel]
    available_silence_strategies: list[SilenceStrategy]
    emotional_baseline: str


@dataclass
class ArcTransition:
    from_state: str
    to_state: str
    trigger_condition: str
    one_way: bool = True


@dataclass
class NPCDefinition:
    """Static NPC configuration loaded from script data."""
    npc_id: str
    name: str
    age: int
    occupation: str
    character_anchor: str  # ~150 chars, injected into every prompt
    personality: PersonalityMatrix
    self_awareness: SelfAwareness
    is_killer: bool

    # Knowledge
    knowledge: list[KnowledgeEntry]

    # Relationships
    relationships: list[Relationship] = field(default_factory=list)

    # Honesty configuration (killer only)
    lie_topics: list[LieTopic] = field(default_factory=list)

    # Silence configuration (non-killer only)
    default_silence_strategy: Optional[SilenceStrategy] = None
    silence_triggers: list[str] = field(default_factory=list)

    # Arc states
    arc_states: list[ArcState] = field(default_factory=list)
    arc_transitions: list[ArcTransition] = field(default_factory=list)
    initial_arc_state: str = ""


@dataclass
class NPCState:
    """Mutable NPC state during a game session."""
    npc_id: str
    current_arc_state: str
    emotional_tag: str  # e.g., "平静", "紧张-中", "愤怒-低", "悲伤-中,懊悔-低"
    attitude_to_player: float  # -1.0 to 1.0
    knowledge_map: dict[str, KnowledgeEntry] = field(default_factory=dict)

    # Fact ledger: records of what was revealed to whom
    fact_ledger: list[dict] = field(default_factory=list)

    # Speech count for rate limiting
    autonomous_speech_count: int = 0

    def get_released_knowledge(self) -> list[KnowledgeEntry]:
        return [k for k in self.knowledge_map.values() if k.released]

    def get_unreleased_knowledge(self) -> list[KnowledgeEntry]:
        return [k for k in self.knowledge_map.values() if not k.released]

    def can_release(self, fact_id: str, condition_met: bool) -> bool:
        entry = self.knowledge_map.get(fact_id)
        if not entry:
            return False
        if entry.released:
            return False
        return condition_met

    def record_release(self, fact_id: str, to_player: str):
        entry = self.knowledge_map.get(fact_id)
        if entry:
            # Dedup: don't re-record if already released to the same player
            if to_player in entry.released_to:
                return
            entry.released = True
            entry.released_to.append(to_player)
            self.fact_ledger.append({
                "fact_id": fact_id,
                "level": entry.level.value,
                "content": entry.content,
                "released_to": to_player,
            })

    def record_autonomous_speech(self, info: str):
        self.fact_ledger.append({
            "type": "autonomous_speech",
            "content": info,
        })
        self.autonomous_speech_count += 1
