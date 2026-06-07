"""Script data models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class DifficultyLevel(str, Enum):
    """Script difficulty levels."""
    EASY = "easy"
    STANDARD = "standard"
    HARD = "hard"


class ScriptType(str, Enum):
    """Script types."""
    BENGGE = "bengge"  # 本格推理
    SOCIAL = "social"  # 社交博弈
    EMOTIONAL = "emotional"  # 情感沉浸


class ScriptBase(BaseModel):
    """Base script model."""
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    script_type: ScriptType
    difficulty: DifficultyLevel
    min_players: int = Field(..., ge=4, le=8)
    max_players: int = Field(..., ge=4, le=8)
    duration_minutes: int = Field(..., ge=60, le=120)
    author: Optional[str] = Field(default="官方编剧", max_length=50)
    tags: List[str] = Field(default_factory=list)
    cover_image: Optional[str] = None
    is_published: bool = False

    @field_validator('max_players')
    @classmethod
    def max_players_must_be_greater_than_min(cls, v: int, info) -> int:
        if 'min_players' in info.data and v < info.data['min_players']:
            raise ValueError('max_players must be greater than or equal to min_players')
        return v


class ScriptCreate(ScriptBase):
    """Script creation model."""
    pass


class ScriptUpdate(BaseModel):
    """Script update model (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    script_type: Optional[ScriptType] = None
    difficulty: Optional[DifficultyLevel] = None
    min_players: Optional[int] = Field(None, ge=4, le=8)
    max_players: Optional[int] = Field(None, ge=4, le=8)
    duration_minutes: Optional[int] = Field(None, ge=60, le=120)
    author: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    cover_image: Optional[str] = None
    is_published: Optional[bool] = None


class ScriptInDB(ScriptBase):
    """Script database model."""
    id: str
    created_at: datetime
    updated_at: datetime
    play_count: int = 0
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    rating_count: int = 0

    class Config:
        from_attributes = True


class ScriptResponse(ScriptBase):
    """Script response model."""
    id: str
    created_at: datetime
    play_count: int
    rating: float
    rating_count: int


class ScriptListParams(BaseModel):
    """Script list query parameters."""
    difficulty: Optional[DifficultyLevel] = None
    script_type: Optional[ScriptType] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    search: Optional[str] = None
    sort_by: str = Field(default="created_at", pattern="^(created_at|rating|play_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class ScriptFilterResult(BaseModel):
    """Script filter result."""
    scripts: List[ScriptResponse]
    total: int
    skip: int
    limit: int
