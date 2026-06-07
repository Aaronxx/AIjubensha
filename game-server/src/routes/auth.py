"""Authentication routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.user import UserCreate, UserLogin, Token
from ..services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    result = await auth_service.register(user_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """Login and get access token."""
    result = await auth_service.login(login_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@router.get("/me", response_model=dict)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info from token."""
    token = credentials.credentials
    user_id = auth_service.verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "is_vip": user.is_vip,
        "stars": user.stars,
        "avatar_url": user.avatar_url
    }


@router.post("/logout", response_model=dict)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout (client should discard token)."""
    # In stateless JWT, we don't need server-side logout
    # But we can add token to blacklist in Redis if needed
    return {"success": True, "message": "Logged out successfully"}
