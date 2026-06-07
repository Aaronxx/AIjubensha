"""Room management service."""
from datetime import datetime, timezone
from typing import Optional, List
from uuid import uuid4

from ..models.room import (
    RoomCreate, RoomUpdate, RoomInDB, RoomResponse, RoomPlayer,
    RoomStatus, RoomSettings, PlayerRole, AISlotConfig
)
from ..services.script_service import script_service


class RoomService:
    """Manages game room operations."""

    def __init__(self):
        # In-memory store for MVP
        self._rooms: dict[str, RoomInDB] = {}
        self._user_rooms: dict[str, str] = {}  # user_id -> room_id (player can only be in one room)

    async def create_room(self, room_data: RoomCreate) -> dict:
        """Create a new game room."""
        # Check if user is already in a room
        if room_data.host_id in self._user_rooms:
            return {
                "success": False,
                "error": "You are already in another room"
            }

        # Validate script exists
        script = await script_service.get_script(room_data.script_id)
        if not script:
            return {
                "success": False,
                "error": "Script not found"
            }

        # Create room
        room_id = str(uuid4())
        now = datetime.now(timezone.utc)

        # Create host player
        host_player = RoomPlayer(
            user_id=room_data.host_id,
            username=room_data.host_username,
            seat_number=1,
            is_ready=True,  # Host is automatically ready
            is_ai=False,
            role_type=PlayerRole.HOST,
            joined_at=now
        )

        room = RoomInDB(
            id=room_id,
            name=room_data.name,
            script_id=room_data.script_id,
            settings=room_data.settings,
            host_id=room_data.host_id,
            host_username=room_data.host_username,
            status=RoomStatus.WAITING,
            players=[host_player],
            max_players=script["max_players"],
            current_players=1,
            created_at=now,
            updated_at=now
        )

        # Store room
        self._rooms[room_id] = room
        self._user_rooms[room_data.host_id] = room_id

        return {
            "success": True,
            "room_id": room_id,
            "room": self._room_to_dict(room)
        }

    async def get_room(self, room_id: str) -> Optional[dict]:
        """Get room by ID."""
        room = self._rooms.get(room_id)
        if not room:
            return None
        return self._room_to_dict(room)

    async def list_rooms(
        self,
        status: Optional[RoomStatus] = None,
        script_id: Optional[str] = None,
        is_private: Optional[bool] = None,
        host_id: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """List rooms with filtering."""
        rooms = list(self._rooms.values())

        # Apply filters
        if status:
            rooms = [r for r in rooms if r.status == status]

        if script_id:
            rooms = [r for r in rooms if r.script_id == script_id]

        if is_private is not None:
            rooms = [r for r in rooms if r.settings.is_private == is_private]

        if host_id:
            rooms = [r for r in rooms if r.host_id == host_id]

        # Sort
        reverse = sort_order == "desc"
        if sort_by == "player_count":
            rooms.sort(key=lambda r: r.current_players, reverse=reverse)
        else:  # created_at
            rooms.sort(key=lambda r: r.created_at, reverse=reverse)

        # Paginate
        rooms = rooms[skip:skip + limit]

        return [self._room_to_dict(r) for r in rooms]

    async def join_room(self, room_id: str, user_id: str, username: str, password: Optional[str] = None) -> dict:
        """Join a room."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        # Check if user is already in this room
        existing_player = next((p for p in room.players if p.user_id == user_id), None)
        if existing_player:
            return {"success": False, "error": "You are already in this room"}

        # Check if user is in another room
        if user_id in self._user_rooms and self._user_rooms[user_id] != room_id:
            return {"success": False, "error": "You are already in another room"}

        # Check room status
        if room.status not in [RoomStatus.WAITING, RoomStatus.READY]:
            return {"success": False, "error": "Room is not accepting new players"}

        # Check password for private rooms
        if room.settings.is_private and room.settings.password != password:
            return {"success": False, "error": "Invalid room password"}

        # Check if room is full
        if room.current_players >= room.max_players:
            return {"success": False, "error": "Room is full"}

        # Find available seat
        occupied_seats = {p.seat_number for p in room.players}
        available_seat = next((i for i in range(1, room.max_players + 1) if i not in occupied_seats), None)

        if available_seat is None:
            return {"success": False, "error": "No available seats"}

        # Add player
        player = RoomPlayer(
            user_id=user_id,
            username=username,
            seat_number=available_seat,
            is_ready=False,
            is_ai=False,
            role_type=PlayerRole.PLAYER,
            joined_at=datetime.now(timezone.utc)
        )

        room.players.append(player)
        room.current_players += 1
        room.updated_at = datetime.now(timezone.utc)
        self._user_rooms[user_id] = room_id

        return {"success": True, "room": self._room_to_dict(room)}

    async def leave_room(self, room_id: str, user_id: str) -> dict:
        """Leave a room."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        player = next((p for p in room.players if p.user_id == user_id), None)
        if not player:
            return {"success": False, "error": "You are not in this room"}

        # Host leaving - close the room
        if player.role_type == PlayerRole.HOST:
            # Remove all players from user_rooms
            for p in room.players:
                if p.user_id in self._user_rooms:
                    del self._user_rooms[p.user_id]
            # Delete room
            del self._rooms[room_id]
            return {"success": True, "message": "Room closed by host"}

        # Regular player leaving
        room.players = [p for p in room.players if p.user_id != user_id]
        room.current_players -= 1
        room.updated_at = datetime.now(timezone.utc)

        if user_id in self._user_rooms:
            del self._user_rooms[user_id]

        return {"success": True, "room": self._room_to_dict(room)}

    async def kick_player(self, room_id: str, host_id: str, target_user_id: str) -> dict:
        """Kick a player from room (host only)."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        # Verify host
        host = next((p for p in room.players if p.user_id == host_id), None)
        if not host or host.role_type != PlayerRole.HOST:
            return {"success": False, "error": "Only host can kick players"}

        # Cannot kick self
        if target_user_id == host_id:
            return {"success": False, "error": "Cannot kick yourself"}

        player = next((p for p in room.players if p.user_id == target_user_id), None)
        if not player:
            return {"success": False, "error": "Player not found in room"}

        # Remove player
        room.players = [p for p in room.players if p.user_id != target_user_id]
        room.current_players -= 1
        room.updated_at = datetime.now(timezone.utc)

        if target_user_id in self._user_rooms:
            del self._user_rooms[target_user_id]

        return {"success": True, "room": self._room_to_dict(room)}

    async def set_player_ready(self, room_id: str, user_id: str, ready: bool = True) -> dict:
        """Set player ready status."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        player = next((p for p in room.players if p.user_id == user_id), None)
        if not player:
            return {"success": False, "error": "You are not in this room"}

        player.is_ready = ready
        room.updated_at = datetime.now(timezone.utc)

        # Check if all players are ready
        if ready and all(p.is_ready for p in room.players if not p.is_ai):
            room.status = RoomStatus.READY

        return {"success": True, "room": self._room_to_dict(room)}

    async def update_room(self, room_id: str, host_id: str, update_data: RoomUpdate) -> dict:
        """Update room settings (host only)."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        # Verify host
        if room.host_id != host_id:
            return {"success": False, "error": "Only host can update room"}

        # Update fields
        if update_data.name:
            room.name = update_data.name
        if update_data.script_id:
            # Validate new script
            script = await script_service.get_script(update_data.script_id)
            if not script:
                return {"success": False, "error": "Script not found"}
            room.script_id = update_data.script_id
            room.max_players = script["max_players"]
        if update_data.settings:
            room.settings = update_data.settings
        if update_data.status:
            room.status = update_data.status

        room.updated_at = datetime.now(timezone.utc)
        return {"success": True, "room": self._room_to_dict(room)}

    async def start_game(self, room_id: str, host_id: str) -> dict:
        """Start the game (host only)."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        if room.host_id != host_id:
            return {"success": False, "error": "Only host can start game"}

        if room.status != RoomStatus.READY:
            return {"success": False, "error": "Room is not ready to start"}

        # Check minimum players
        human_players = [p for p in room.players if not p.is_ai]
        if len(human_players) < room.settings.min_players:
            return {"success": False, "error": f"Need at least {room.settings.min_players} players"}

        room.status = RoomStatus.PLAYING
        room.updated_at = datetime.now(timezone.utc)

        return {"success": True, "room": self._room_to_dict(room)}

    async def add_ai_slot(self, room_id: str, host_id: str, config: AISlotConfig) -> dict:
        """Add AI player to room."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        if room.host_id != host_id:
            return {"success": False, "error": "Only host can add AI"}

        if not room.settings.ai_fill:
            return {"success": False, "error": "AI fill is disabled"}

        if room.current_players >= room.max_players:
            return {"success": False, "error": "Room is full"}

        # Check seat availability
        occupied_seats = {p.seat_number for p in room.players}
        if config.seat_number in occupied_seats:
            return {"success": False, "error": "Seat is already occupied"}

        # Add AI player
        ai_player = RoomPlayer(
            user_id=f"ai_{config.ai_character_id}",
            username=config.ai_character_name,
            seat_number=config.seat_number,
            is_ready=True,  # AI is always ready
            is_ai=True,
            role_type=PlayerRole.PLAYER,
            joined_at=datetime.now(timezone.utc)
        )

        room.players.append(ai_player)
        room.current_players += 1
        room.updated_at = datetime.now(timezone.utc)

        return {"success": True, "room": self._room_to_dict(room)}

    async def remove_ai_slot(self, room_id: str, host_id: str, seat_number: int) -> dict:
        """Remove AI player from room."""
        room = self._rooms.get(room_id)
        if not room:
            return {"success": False, "error": "Room not found"}

        if room.host_id != host_id:
            return {"success": False, "error": "Only host can remove AI"}

        ai_player = next((p for p in room.players if p.is_ai and p.seat_number == seat_number), None)
        if not ai_player:
            return {"success": False, "error": "AI player not found at this seat"}

        room.players = [p for p in room.players if not (p.is_ai and p.seat_number == seat_number)]
        room.current_players -= 1
        room.updated_at = datetime.now(timezone.utc)

        return {"success": True, "room": self._room_to_dict(room)}

    async def get_room_by_user(self, user_id: str) -> Optional[dict]:
        """Get room by user ID."""
        room_id = self._user_rooms.get(user_id)
        if not room_id:
            return None
        return await self.get_room(room_id)

    def _room_to_dict(self, room: RoomInDB) -> dict:
        """Convert room to dict."""
        return {
            "id": room.id,
            "name": room.name,
            "script_id": room.script_id,
            "settings": {
                "speak_mode": room.settings.speak_mode,
                "ai_fill": room.settings.ai_fill,
                "min_players": room.settings.min_players,
                "is_private": room.settings.is_private,
                "has_password": room.settings.password is not None
            },
            "host_id": room.host_id,
            "host_username": room.host_username,
            "status": room.status.value,
            "players": [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "avatar": p.avatar,
                    "seat_number": p.seat_number,
                    "is_ready": p.is_ready,
                    "is_ai": p.is_ai,
                    "role_type": p.role_type.value,
                    "game_role": p.game_role,
                    "joined_at": p.joined_at.isoformat()
                }
                for p in room.players
            ],
            "max_players": room.max_players,
            "current_players": room.current_players,
            "created_at": room.created_at.isoformat(),
            "updated_at": room.updated_at.isoformat(),
            "game_session_id": room.game_session_id
        }


# Singleton instance
room_service = RoomService()
