"""Dialogue system models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MessageType(str, Enum):
    """Message types in dialogue."""
    PLAYER = "player"
    NPC = "npc"
    SYSTEM = "system"
    PRIVATE = "private"


class DialogueMessage(BaseModel):
    """Single dialogue message."""
    message_id: str
    session_id: str
    room_id: str
    sender_id: str
    sender_name: str
    sender_type: MessageType
    content: str
    timestamp: datetime
    target_id: Optional[str] = None  # For private messages
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NPCResponseMetadata(BaseModel):
    """NPC response metadata."""
    emotional_tag: str
    info_revealed: List[Dict[str, Any]]
    attitude_shift: Optional[str] = None
    arc_state_transition: Optional[str] = None
    info_revealed_levels: List[int] = Field(default_factory=list)


class DialogueContext(BaseModel):
    """Assembled context for NPC prompt."""
    character_id: str
    character_anchor: str
    current_act: str
    arc_state: str
    emotional_tag: str
    knowledge_released: List[str]
    knowledge_hidden: List[str]
    honesty_mode: str  # "truth", "lie", "avoid"
    lie_topics: List[str]
    silence_strategy: str
    recent_context: List[Dict[str, Any]]
    fact_ledger: List[Dict[str, Any]]
    attitude_to_player: float


class PromptBuildResult(BaseModel):
    """Built prompt result."""
    system_prompt: str
    user_message: str
    character_id: str


class StructuredNPCOutput(BaseModel):
    """Expected structured output from NPC."""
    reply: str
    emotional_tag: str
    info_revealed: List[Dict[str, str]]
    attitude_shift: Optional[str] = None
    arc_state_transition: Optional[str] = None


class DialogueStateUpdate(BaseModel):
    """State update after dialogue."""
    character_id: str
    new_emotional_tag: str
    info_released: List[str]
    attitude_changes: Dict[str, float]
    arc_transition: Optional[str] = None


class NPCAutonomousTrigger(BaseModel):
    """Trigger for NPC autonomous speech."""
    trigger_type: str  # "mentioned", "time_elapsed", "emotion_threshold", "conflict"
    source_message_id: Optional[str] = None
    target_player_id: Optional[str] = None
    urgency: int = Field(..., ge=1, le=5)


class SpeechQuota(BaseModel):
    """NPC speech quota for current act."""
    character_id: str
    act: str
    max_speeches: int
    used_speeches: int
    remaining_speeches: int


class PrivateChatRequest(BaseModel):
    """Request to start private chat with NPC."""
    player_id: str
    npc_id: str
    initial_message: str


class PrivateChatSession(BaseModel):
    """Active private chat session."""
    session_id: str
    player_id: str
    npc_id: str
    started_at: datetime
    message_count: int = 0
    is_active: bool = True


class DialogueSummary(BaseModel):
    """Summary of dialogue for a session."""
    session_id: str
    total_messages: int
    player_message_count: int
    npc_message_count: int
    key_revelations: List[str]
    emotional_journey: List[Dict[str, Any]]


class HonestyRule(BaseModel):
    """Honesty rule configuration."""
    is_murderer: bool
    can_lie_on: List[str]
    must_tell_truth_on: List[str]
    can_avoid: bool
    avoidance_strategy: str


class DialogueFilterParams(BaseModel):
    """Dialogue filtering parameters."""
    session_id: Optional[str] = None
    room_id: Optional[str] = None
    sender_id: Optional[str] = None
    sender_type: Optional[MessageType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class DialogueExportResult(BaseModel):
    """Dialogue export result."""
    messages: List[DialogueMessage]
    total: int
    has_more: bool
