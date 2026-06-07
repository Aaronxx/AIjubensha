"""Game session data models."""
from dataclasses import dataclass, field
from enum import Enum


class GamePhase(Enum):
    PREPARATION = "preparation"
    ACT_1_TURN_TALK = "act_1_turn"
    ROUND_1_SEARCH = "round_1_search"
    ACT_2_DISCUSS = "act_2_discuss"
    DETECTIVE_VOTE = "detective_vote"
    ROUND_2_SEARCH = "round_2_search"
    ACT_3_DISCUSS = "act_3_discuss"
    FINAL_VOTE = "final_vote"
    RESULT = "result"
    FINISHED = "finished"


class PlayerRole(Enum):
    NORMAL = "normal"
    DETECTIVE = "detective"
    KILLER = "killer"


@dataclass
class PlayerSession:
    player_id: str
    character_id: str
    role: PlayerRole
    is_ai: bool = False
    ap_remaining: int = 0
    speech_count: int = 0
    speech_limit: int = 15
    question_count: dict = field(default_factory=dict)
    question_limit_per_player: int = 3
    has_confirmed: bool = False
    vote_target: str | None = None
    clues_discovered: list[str] = field(default_factory=list)
    clues_public: list[str] = field(default_factory=list)
