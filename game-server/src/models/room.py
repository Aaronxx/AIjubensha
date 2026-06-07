"""Room data models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class RoomStatus(str, Enum):
    """Room status states."""
    WAITING = "waiting"      # 等待中，可加入
    READY = "ready"          # 准备就绪，即将开始
    PLAYING = "playing"      # 游戏中
    FINISHED = "finished"    # 已结束


class PlayerRole(str, Enum):
    """Player roles in game."""
    HOST = "host"            # 房主
    PLAYER = "player"        # 普通玩家
    DETECTIVE = "detective"  # 侦探（游戏内身份）
    MURDERER = "murderer"    # 凶手（游戏内身份）
    NORMAL = "normal"        # 普通角色（游戏内身份）


class RoomPlayer(BaseModel):
    """Player in room."""
    user_id: str
    username: str
    avatar: Optional[str] = None
    seat_number: int                        # 座位号 1-8
    is_ready: bool = False                  # 是否准备
    is_ai: bool = False                     # 是否为AI
    role_type: PlayerRole = PlayerRole.PLAYER  # 房间角色
    game_role: Optional[str] = None         # 分配的游戏角色ID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomSettings(BaseModel):
    """Room settings."""
    # 发言模式
    speak_mode: str = Field(default="turn", pattern="^(turn|free)$")  # turn=轮流, free=自由
    # AI补位
    ai_fill: bool = True                    # 人数不足时AI补位
    # 最低人数
    min_players: int = Field(default=4, ge=1, le=8)
    # 是否为私密房间
    is_private: bool = False
    # 房间密码（私密房间）
    password: Optional[str] = None


class RoomBase(BaseModel):
    """Base room model."""
    name: str = Field(..., min_length=1, max_length=50)
    script_id: str                        # 选择的剧本ID
    settings: RoomSettings = Field(default_factory=RoomSettings)


class RoomCreate(RoomBase):
    """Room creation model."""
    host_id: str                          # 房主用户ID
    host_username: str                    # 房主用户名


class RoomUpdate(BaseModel):
    """Room update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    script_id: Optional[str] = None
    settings: Optional[RoomSettings] = None
    status: Optional[RoomStatus] = None


class RoomInDB(RoomBase):
    """Room database model."""
    id: str                               # 房间ID
    host_id: str                          # 房主用户ID
    host_username: str                    # 房主用户名
    status: RoomStatus = RoomStatus.WAITING
    players: List[RoomPlayer] = Field(default_factory=list)
    max_players: int = 8                  # 从剧本读取
    current_players: int = 0              # 当前玩家数（含AI）
    created_at: datetime
    updated_at: datetime
    game_session_id: Optional[str] = None  # 关联的游戏会话ID

    model_config = ConfigDict(from_attributes=True)


class RoomResponse(RoomBase):
    """Room response model."""
    id: str
    host_id: str
    host_username: str
    status: RoomStatus
    players: List[RoomPlayer]
    max_players: int
    current_players: int
    created_at: datetime
    updated_at: datetime


class RoomListParams(BaseModel):
    """Room list query parameters."""
    status: Optional[RoomStatus] = None
    script_id: Optional[str] = None
    is_private: Optional[bool] = None
    host_id: Optional[str] = None
    sort_by: str = Field(default="created_at", pattern="^(created_at|player_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class RoomJoinRequest(BaseModel):
    """Room join request."""
    password: Optional[str] = None        # 私密房间密码
    # Optional: player info for game session (used in tests / game flow)
    player_id: Optional[str] = None
    character_id: Optional[str] = None
    role: Optional[str] = None


class RoomPlayerAction(BaseModel):
    """Player action in room."""
    action: str = Field(..., pattern="^(ready|unready|leave|kick)$")
    target_user_id: Optional[str] = None  # 用于踢人


class AISlotConfig(BaseModel):
    """AI slot configuration."""
    seat_number: int
    ai_character_id: str                  # AI角色ID
    ai_character_name: str                # AI角色名称


class RoomFilterResult(BaseModel):
    """Room filter result."""
    rooms: List[RoomResponse]
    total: int
    skip: int
    limit: int
