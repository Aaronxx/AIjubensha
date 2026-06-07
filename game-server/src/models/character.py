"""Character/NPC data models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CharacterType(str, Enum):
    """NPC self-awareness types."""
    OMNISCIENT = "omniscient"          # 全知型 - 亲手作案，未失忆
    PROGRESSIVE = "progressive"       # 渐进发现型 - 失忆设定
    UNAWARE = "unaware"               # 全程不知型 - 被利用/间接作案
    ACCOMPLICE = "accomplice"         # 多人共犯型 - 东方快车式
    SCAPEGOAT = "scapegoat"           # 替罪羊型 - 被陷害


class SilenceStrategy(str, Enum):
    """Silence/avoidance strategies."""
    HARD_SILENCE = "hard_silence"           # 硬沉默
    POLITE_REFUSAL = "polite_refusal"       # 委婉拒绝
    TOPIC_SHIFT = "topic_shift"             # 转移话题
    EVASION = "evasion"                     # 顾左右而言他
    EMOTIONAL = "emotional"                 # 情绪回避


class PersonalityDimension(BaseModel):
    """Single personality dimension (0.0 - 1.0 scale)."""
    value: float = Field(..., ge=0.0, le=1.0)
    description: str


class PersonalityMatrix(BaseModel):
    """5-dimensional personality matrix."""
    extroversion: PersonalityDimension      # 外向←→内向
    aggressiveness: PersonalityDimension    # 攻击性←→合作性
    honesty: PersonalityDimension           # 诚实←→欺骗倾向
    rationality: PersonalityDimension       # 理性←→情绪化
    speaking_style: str                     # 说话风格描述


class KnowledgeEntry(BaseModel):
    """Single knowledge/fact entry."""
    fact_id: str
    content: str
    level: int = Field(..., ge=1, le=4)     # L1-L4 information level
    release_condition: str                  # 何时可以释放此信息
    is_secret: bool = False                 # 是否为必须隐藏的秘密


class GoalSystem(BaseModel):
    """Character goals and boundaries."""
    primary_goal: str                       # 首要目标（必须达成）
    secondary_goals: List[str] = Field(default_factory=list)  # 次要目标
    red_lines: List[str] = Field(default_factory=list)          # 红线（绝不做的事）
    attitude_to_others: Dict[str, float] = Field(default_factory=dict)  # 对其他角色态度


class ArcState(BaseModel):
    """Single state in character arc."""
    state_id: str
    name: str
    description: str
    attitude_modifier: float                # 态度调整
    info_release_levels: List[int]          # 可释放信息层级
    silence_strategy: SilenceStrategy


class ArcTransition(BaseModel):
    """Transition between arc states."""
    from_state: str
    to_state: str
    trigger_condition: str                  # 触发条件
    required_attitude: Optional[float] = None
    required_emotion: Optional[str] = None


class CharacterRoleInScript(BaseModel):
    """Character's role in a specific script."""
    is_murderer: bool = False
    character_type: CharacterType
    self_awareness: str                     # 自我认知描述
    lie_topics: List[str] = Field(default_factory=list)      # 可撒谎的话题
    protected_info: List[str] = Field(default_factory=list)   # 受保护信息


class RelationshipEntry(BaseModel):
    """Relationship with another character."""
    target_character_id: str
    relationship_type: str                  # 情侣/战友/敌对/中立
    will_cover: bool = False                # 是否会替对方遮掩
    will_lie_for: bool = False              # 是否会为对方撒谎
    will_take_blame: bool = False          # 是否会替对方挡刀


class CharacterBase(BaseModel):
    """Base character model."""
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=1, le=150)
    occupation: str = Field(..., max_length=50)
    background: str = Field(..., max_length=500)
    avatar: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Character creation model."""
    personality: PersonalityMatrix
    knowledge: List[KnowledgeEntry]
    goals: GoalSystem
    arc_states: List[ArcState]
    arc_transitions: List[ArcTransition]
    default_silence_strategy: SilenceStrategy
    character_anchor: str = Field(..., min_length=50, max_length=300)  # 性格锚点


class CharacterUpdate(BaseModel):
    """Character update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    age: Optional[int] = Field(None, ge=1, le=150)
    occupation: Optional[str] = Field(None, max_length=50)
    background: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None
    personality: Optional[PersonalityMatrix] = None
    character_anchor: Optional[str] = Field(None, min_length=50, max_length=300)


class CharacterInDB(CharacterBase):
    """Character database model."""
    id: str
    personality: PersonalityMatrix
    knowledge: List[KnowledgeEntry]
    goals: GoalSystem
    arc_states: List[ArcState]
    arc_transitions: List[ArcTransition]
    current_arc_state: str                  # 当前弧状态ID
    default_silence_strategy: SilenceStrategy
    character_anchor: str
    relationships: List[RelationshipEntry] = Field(default_factory=list)
    script_assignments: Dict[str, CharacterRoleInScript] = Field(default_factory=dict)  # script_id -> role
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0                    # 被使用次数

    model_config = ConfigDict(from_attributes=True)


class CharacterResponse(CharacterBase):
    """Character response model."""
    id: str
    personality: PersonalityMatrix
    character_anchor: str
    current_arc_state: str
    usage_count: int
    created_at: datetime


class CharacterDetailResponse(CharacterBase):
    """Detailed character response for editing."""
    id: str
    personality: PersonalityMatrix
    knowledge: List[KnowledgeEntry]
    goals: GoalSystem
    arc_states: List[ArcState]
    arc_transitions: List[ArcTransition]
    default_silence_strategy: SilenceStrategy
    character_anchor: str
    relationships: List[RelationshipEntry]
    script_assignments: Dict[str, CharacterRoleInScript]
    usage_count: int
    created_at: datetime
    updated_at: datetime


class CharacterScriptAssignment(BaseModel):
    """Assign character to script."""
    script_id: str
    role: CharacterRoleInScript


class CharacterFilterResult(BaseModel):
    """Character filter result."""
    characters: List[CharacterResponse]
    total: int
    skip: int
    limit: int


class EmotionalState(BaseModel):
    """Current emotional state."""
    primary_emotion: str                    # 主要情绪
    intensity: float = Field(..., ge=0.0, le=1.0)  # 强度
    trigger: Optional[str] = None           # 触发原因
    timestamp: datetime


class CharacterStateSnapshot(BaseModel):
    """Snapshot of character state during game."""
    character_id: str
    current_arc_state: str
    emotional_tag: EmotionalState
    knowledge_released: List[str]           # 已释放的fact_ids
    attitude_to_players: Dict[str, float]  # 对各玩家态度
    fact_ledger: List[Dict[str, Any]]       # 事实账本记录
