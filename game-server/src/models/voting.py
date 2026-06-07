"""Voting system models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class VoteType(str, Enum):
    """Type of vote."""
    DETECTIVE_MID = "detective_mid"    # 侦探中期投票
    FINAL = "final"                    # 最终投票


class Vote(BaseModel):
    """Single vote."""
    vote_id: str
    session_id: str
    voter_id: str
    voter_name: str
    target_id: str                    # 投票目标（玩家ID）
    target_name: str
    vote_type: VoteType
    timestamp: datetime
    is_valid: bool = True


class VoteSession(BaseModel):
    """Voting session."""
    session_id: str
    game_session_id: str
    vote_type: VoteType
    status: str = "waiting"           # waiting, active, finished
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    votes: List[Vote] = Field(default_factory=list)
    voter_count: int = 0              # 应投票人数
    voted_count: int = 0              # 已投票人数
    result: Optional[Dict] = None   # 投票结果


class DetectiveVoteRequest(BaseModel):
    """Detective mid-game vote request."""
    target_id: str                    # 嫌疑人ID


class FinalVoteRequest(BaseModel):
    """Final vote request."""
    target_id: str                    # 指认的凶手ID


class VoteResult(BaseModel):
    """Vote result."""
    success: bool
    vote_type: VoteType
    total_votes: int
    results: Dict[str, int]           # target_id -> vote_count
    winner: Optional[str] = None    # 得票最高者
    winner_votes: int = 0
    is_tie: bool = False
    tie_players: List[str] = Field(default_factory=list)
    message: Optional[str] = None    # 结果说明消息


class VoteStatistics(BaseModel):
    """Vote statistics for a player."""
    player_id: str
    total_votes_cast: int = 0         # 总投票次数
    correct_votes: int = 0            # 正确投票次数
    accuracy_rate: float = 0.0       # 正确率
    as_detective_success: int = 0     # 作为侦探成功次数
    as_detective_total: int = 0       # 作为侦探总次数
    as_murderer_escaped: int = 0    # 作为凶手逃脱次数
    as_murderer_caught: int = 0     # 作为凶手被抓次数


class TieBreakerVote(BaseModel):
    """Tie breaker vote."""
    voter_id: str
    target_id: str
    timestamp: datetime


class TieBreakerSession(BaseModel):
    """Tie breaker session."""
    original_session_id: str
    tied_players: List[str]
    votes: List[TieBreakerVote] = Field(default_factory=list)
    status: str = "active"
    result: Optional[str] = None      # 胜出者ID


class VoteRevealSequence(BaseModel):
    """Vote reveal sequence for final voting."""
    zero_vote_players: List[str]      # 0票玩家
    low_vote_players: List[str]       # 1-2票玩家
    high_vote_players: List[str]      # 最高票玩家
    final_result: str                 # 最终结果
