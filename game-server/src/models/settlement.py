"""Settlement and achievement system models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GameResult(str, Enum):
    """Game result type."""
    VICTORY = "victory"           # 胜利（投对凶手）
    DEFEAT = "defeat"             # 失败（投错凶手）
    ESCAPE = "escape"             # 凶手逃脱
    CAUGHT = "caught"             # 凶手被抓


class PlayerRole(str, Enum):
    """Player role in game."""
    DETECTIVE = "detective"       # 侦探
    MURDERER = "murderer"         # 凶手
    CIVILIAN = "civilian"         # 普通玩家


class SettlementRecord(BaseModel):
    """Game settlement record."""
    settlement_id: str
    game_session_id: str
    script_id: str
    script_name: str
    player_id: str
    player_name: str
    character_id: str
    character_name: str
    role: PlayerRole
    result: GameResult
    voted_correctly: bool         # 是否投对
    is_murderer: bool = False    # 是否是凶手
    escaped: Optional[bool] = None  # 凶手是否逃脱
    vote_target: Optional[str] = None  # 投票给了谁
    actual_murderer: Optional[str] = None  # 真实凶手

    # 游戏表现数据
    ap_spent: int = 0             # 使用的AP
    clues_discovered: int = 0     # 发现的线索数
    clues_revealed: int = 0       # 公开的线索数
    messages_sent: int = 0        # 发言次数
    private_chats: int = 0        # 私聊次数

    # 时间记录
    game_duration_minutes: int = 0  # 游戏时长（分钟）
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class PlayerStats(BaseModel):
    """Player cumulative statistics."""
    player_id: str

    # 总局数
    total_games: int = 0
    games_as_detective: int = 0
    games_as_murderer: int = 0
    games_as_civilian: int = 0

    # 胜率统计（普通玩家）
    correct_votes: int = 0
    incorrect_votes: int = 0
    vote_accuracy: float = 0.0   # 投票正确率

    # 侦探统计
    detective_games: int = 0
    detective_success: int = 0   # 作为侦探成功次数
    detective_rate: float = 0.0   # 侦探成功率

    # 凶手统计
    murderer_games: int = 0
    murderer_escapes: int = 0    # 逃脱次数
    escape_rate: float = 0.0      # 逃脱率

    # 游戏数据累计
    total_ap_spent: int = 0
    total_clues_discovered: int = 0
    total_messages_sent: int = 0
    total_game_time_minutes: int = 0

    # 成就相关
    achievements_unlocked: List[str] = Field(default_factory=list)
    stars_earned: int = 0

    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class AchievementRarity(str, Enum):
    """Achievement rarity level."""
    COMMON = "common"             # 普通
    RARE = "rare"                 # 稀有
    EPIC = "epic"                 # 史诗
    LEGENDARY = "legendary"       # 传说
    HIDDEN = "hidden"             # 隐藏


class Achievement(BaseModel):
    """Achievement definition."""
    achievement_id: str
    name: str
    description: str
    rarity: AchievementRarity
    icon: Optional[str] = None    # 图标URL或标识
    condition_type: str           # 触发条件类型
    condition_value: Dict[str, Any]  # 条件参数
    reward_stars: int = 0         # 奖励星星数
    is_hidden: bool = False       # 是否隐藏成就
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class PlayerAchievement(BaseModel):
    """Player unlocked achievement."""
    player_id: str
    achievement_id: str
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now())
    game_session_id: Optional[str] = None  # 在哪局游戏中解锁


class SettlementSummary(BaseModel):
    """Settlement summary for a game."""
    game_session_id: str
    script_id: str
    script_name: str

    # 参与玩家
    players: List[SettlementRecord]

    # 游戏结果
    murderer_id: str
    murderer_name: str
    murderer_caught: bool         # 是否被指认
    votes_for_murderer: int = 0   # 投给凶手的票数

    # 统计数据
    total_duration_minutes: int = 0
    total_clues_discovered: int = 0
    total_messages: int = 0

    # MVP
    mvp_player_id: Optional[str] = None  # 表现最佳玩家

    created_at: datetime = Field(default_factory=lambda: datetime.now())


class SettlementRequest(BaseModel):
    """Request to settle a game."""
    game_session_id: str
    murderer_id: str              # 真实凶手ID
    votes: Dict[str, str]         # voter_id -> target_id


class PlayerRankEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    player_id: str
    player_name: str
    avatar_url: Optional[str] = None
    score: float                  # 综合评分
    stats: Dict[str, Any]         # 具体统计数据


class LeaderboardCategory(str, Enum):
    """Leaderboard category."""
    INVESTIGATION = "investigation"   # 推理榜
    SOCIAL = "social"                 # 社交榜
    CONTRIBUTION = "contribution"     # 贡献榜
    OVERALL = "overall"               # 综合榜
