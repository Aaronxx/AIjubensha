"""User data models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(BaseModel):
    """User registration model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """User database model."""
    id: str
    hashed_password: str
    is_active: bool = True
    is_vip: bool = False
    stars: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response model."""
    id: str
    is_vip: bool = False
    stars: int = 0
    created_at: datetime


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload model."""
    sub: Optional[str] = None
    exp: Optional[datetime] = None
