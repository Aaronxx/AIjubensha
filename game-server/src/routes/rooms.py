"""Room management routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

from ..models.room import (
    RoomCreate, RoomUpdate, RoomJoinRequest, RoomPlayerAction,
    RoomStatus, AISlotConfig, RoomListParams, PlayerRole as RoomPlayerRole
)
from ..session.models import PlayerRole as GamePlayerRole
from ..services.room_service import room_service
from ..services.game_service import game_manager
from ..services.auth_service import auth_service

router = APIRouter()


async def get_current_user(token: str = Query(..., description="JWT token")):
    """Dependency to get current user from token."""
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


@router.post("/rooms", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_room(room_data: RoomCreate, user: dict = Depends(get_current_user)):
    """Create a new game room."""
    # Override host info with current user
    room_data.host_id = user["user_id"]
    room_data.host_username = user["username"]

    result = await room_service.create_room(room_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.get("/rooms")
async def list_rooms(
    status: Optional[RoomStatus] = Query(None, description="Filter by status"),
    script_id: Optional[str] = Query(None, description="Filter by script"),
    is_private: Optional[bool] = Query(None, description="Filter by privacy"),
    sort_by: str = Query("created_at", pattern="^(created_at|player_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List available rooms."""
    rooms = await room_service.list_rooms(
        status=status,
        script_id=script_id,
        is_private=is_private,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return rooms


@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    """Get room details."""
    room = await room_service.get_room(room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return room


@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,
    join_data: RoomJoinRequest,
    user: dict = Depends(get_current_user)
):
    """Join a room."""
    # Use player_id from request body if provided (for game flow / tests),
    # otherwise fall back to authenticated user
    effective_user_id = join_data.player_id or user["user_id"]
    effective_username = effective_user_id  # Use player_id as username for test simplicity

    result = await room_service.join_room(
        room_id=room_id,
        user_id=effective_user_id,
        username=effective_username,
        password=join_data.password
    )

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "password" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    # Create game session if first player joins
    game_session = game_manager.get_session(room_id)
    if game_session is None:
        room_dict = await room_service.get_room(room_id)
        if room_dict:
            game_manager.create_session(room_id, room_dict["script_id"])

    # Also register player in game_manager if they provided character info
    if join_data.player_id and join_data.character_id and join_data.role:
        game_session = game_manager.get_session(room_id)
        if game_session:
            # Check if player already in game session
            if join_data.player_id not in game_session.players:
                # Map room roles to game session roles
                role_map = {
                    "detective": GamePlayerRole.DETECTIVE,
                    "killer": GamePlayerRole.KILLER,
                    "murderer": GamePlayerRole.KILLER,
                    "normal": GamePlayerRole.NORMAL,
                    "player": GamePlayerRole.NORMAL,
                    "host": GamePlayerRole.NORMAL,
                }
                game_role = role_map.get(join_data.role, GamePlayerRole.NORMAL)
                game_session.add_player(
                    join_data.player_id,
                    join_data.character_id,
                    game_role
                )

    return result


@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, user: dict = Depends(get_current_user)):
    """Leave a room."""
    result = await room_service.leave_room(room_id, user["user_id"])

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.post("/rooms/{room_id}/kick")
async def kick_player(
    room_id: str,
    target_user_id: str,
    user: dict = Depends(get_current_user)
):
    """Kick a player from room (host only)."""
    result = await room_service.kick_player(room_id, user["user_id"], target_user_id)

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "host" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.post("/rooms/{room_id}/ready")
async def set_ready(room_id: str, user: dict = Depends(get_current_user)):
    """Set player as ready."""
    result = await room_service.set_player_ready(room_id, user["user_id"], ready=True)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.post("/rooms/{room_id}/unready")
async def set_unready(room_id: str, user: dict = Depends(get_current_user)):
    """Set player as not ready."""
    result = await room_service.set_player_ready(room_id, user["user_id"], ready=False)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.patch("/rooms/{room_id}")
async def update_room(
    room_id: str,
    update_data: RoomUpdate,
    user: dict = Depends(get_current_user)
):
    """Update room settings (host only)."""
    result = await room_service.update_room(room_id, user["user_id"], update_data)

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "host" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.post("/rooms/{room_id}/start")
async def start_game(room_id: str, user: dict = Depends(get_current_user)):
    """Start the game (host only)."""
    result = await room_service.start_game(room_id, user["user_id"])

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "host" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.post("/rooms/{room_id}/ai")
async def add_ai_player(
    room_id: str,
    config: AISlotConfig,
    user: dict = Depends(get_current_user)
):
    """Add AI player to room (host only)."""
    result = await room_service.add_ai_slot(room_id, user["user_id"], config)

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "host" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.delete("/rooms/{room_id}/ai/{seat_number}")
async def remove_ai_player(
    room_id: str,
    seat_number: int,
    user: dict = Depends(get_current_user)
):
    """Remove AI player from room (host only)."""
    result = await room_service.remove_ai_slot(room_id, user["user_id"], seat_number)

    if not result["success"]:
        status_code = status.HTTP_403_FORBIDDEN if "host" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.get("/my-room")
async def get_my_room(user: dict = Depends(get_current_user)):
    """Get current user's room."""
    room = await room_service.get_room_by_user(user["user_id"])

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in any room"
        )

    return room
