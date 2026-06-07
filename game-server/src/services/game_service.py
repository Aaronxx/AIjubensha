"""In-memory game session manager."""
from __future__ import annotations
import uuid
from ..session.state_machine import GameSession
from ..session.models import PlayerRole


class GameManager:
    """Manages all active game sessions (in-memory for MVP)."""

    def __init__(self):
        self._sessions: dict[str, GameSession] = {}
        self._rooms: dict[str, dict] = {}

    def create_room(self, script_id: str, room_name: str, max_players: int = 6) -> dict:
        room_id = str(uuid.uuid4())[:8]
        room = {
            "room_id": room_id,
            "script_id": script_id,
            "room_name": room_name,
            "max_players": max_players,
            "players": [],
            "status": "waiting",
        }
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> dict | None:
        return self._rooms.get(room_id)

    def list_rooms(self) -> list[dict]:
        return list(self._rooms.values())

    def join_room(self, room_id: str, player_id: str, character_id: str, role: str) -> dict | None:
        room = self._rooms.get(room_id)
        if not room:
            return None
        if len(room["players"]) >= room["max_players"]:
            return None
        role_enum = PlayerRole(role)
        room["players"].append({
            "player_id": player_id,
            "character_id": character_id,
            "role": role,
            "is_ai": False,
        })
        # Create session when first player joins
        if room_id not in self._sessions:
            self._sessions[room_id] = GameSession(room_id, room["script_id"])
        self._sessions[room_id].add_player(player_id, character_id, role_enum)
        return room

    def get_session(self, room_id: str) -> GameSession | None:
        return self._sessions.get(room_id)

    def create_session(self, room_id: str, script_id: str) -> GameSession:
        """Create a game session for an existing room."""
        if room_id not in self._sessions:
            self._sessions[room_id] = GameSession(room_id, script_id)
        return self._sessions[room_id]


# Singleton
game_manager = GameManager()
