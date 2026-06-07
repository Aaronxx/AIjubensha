"""Investigation system models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class InvestigationTargetStatus(str, Enum):
    """Investigation target status."""
    LOCKED = "locked"           # 未解锁
    AVAILABLE = "available"     # 可调查
    PARTIAL = "partial"         # 部分完成
    COMPLETED = "completed"      # 已完成


class ClueLevel(int, Enum):
    """Clue information level."""
    LEVEL_1 = 1     # 表面线索
    LEVEL_2 = 2     # 基础线索
    LEVEL_3 = 3     # 深层线索
    LEVEL_4 = 4     # 核心秘密


class ClueRevealOrder(BaseModel):
    """Clue reveal order based on AP investment."""
    clue_id: str
    ap_required: int            # 需要多少AP才能发现此线索
    is_revealed: bool = False
    revealed_by: Optional[str] = None  # 被谁发现


class InvestigationTarget(BaseModel):
    """Investigation target."""
    target_id: str
    name: str
    description: str
    location: str
    ap_required: int           # 完成调查所需AP
    ap_invested: int = 0       # 已投入AP
    status: InvestigationTargetStatus = InvestigationTargetStatus.LOCKED
    unlock_condition: Optional[Dict[str, Any]] = None  # 解锁条件
    clues: List[ClueRevealOrder] = Field(default_factory=list)
    clue_level: ClueLevel = ClueLevel.LEVEL_1


class Clue(BaseModel):
    """Clue data model."""
    clue_id: str
    title: str
    description: str
    location: str
    level: ClueLevel
    evidence_type: str         # 物证/证言/文件/痕迹等
    image_url: Optional[str] = None
    unlocks: List[str] = Field(default_factory=list)  # 解锁的其他target_ids
    related_characters: List[str] = Field(default_factory=list)


class DiscoveredClue(BaseModel):
    """Player discovered clue."""
    clue_id: str
    discovered_at: datetime
    discovered_by: str         # player_id
    is_public: bool = False   # 是否公开
    revealed_at: Optional[datetime] = None


class InvestigationRound(BaseModel):
    """Investigation round data."""
    round_number: int
    ap_per_player: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "waiting"   # waiting, active, finished


class PlayerInvestigationState(BaseModel):
    """Player's investigation state."""
    player_id: str
    total_ap: int = 0
    remaining_ap: int = 0
    discovered_clues: List[DiscoveredClue] = Field(default_factory=list)
    investigated_targets: List[str] = Field(default_factory=list)
    total_ap_spent: int = 0


class SessionInvestigation(BaseModel):
    """Investigation state for a game session."""
    session_id: str
    current_round: int = 1
    max_rounds: int = 2
    rounds: List[InvestigationRound] = Field(default_factory=list)
    targets: List[InvestigationTarget] = Field(default_factory=list)
    player_states: Dict[str, PlayerInvestigationState] = Field(default_factory=dict)
    public_clues: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class InvestRequest(BaseModel):
    """Request to investigate a target."""
    target_id: str
    ap_to_spend: int = Field(..., ge=1)


class RevealClueRequest(BaseModel):
    """Request to reveal a clue."""
    clue_id: str
    reveal_to_public: bool = True


class InvestigationResult(BaseModel):
    """Investigation result."""
    success: bool
    target_id: str
    ap_spent: int
    ap_remaining: int
    clues_discovered: List[str] = Field(default_factory=list)
    new_unlocks: List[str] = Field(default_factory=list)
    message: str


class ClueDetailResponse(BaseModel):
    """Clue detail response."""
    clue_id: str
    title: str
    description: str
    location: str
    level: int
    evidence_type: str
    discovered_by: str
    discovered_at: datetime
    is_public: bool


class InvestigationSummary(BaseModel):
    """Summary of investigation for session."""
    session_id: str
    current_round: int
    total_clues: int
    public_clues: int
    player_progress: List[PlayerInvestigationState]
    available_targets: List[InvestigationTarget]
    locked_targets: List[InvestigationTarget]
