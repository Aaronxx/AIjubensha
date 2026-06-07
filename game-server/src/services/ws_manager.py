"""WebSocket connection manager for group chat."""
from fastapi import WebSocket


class WSManager:
    def __init__(self):
        self._connections: dict[str, dict[str, WebSocket]] = {}  # {room_id: {player_id: ws}}

    async def connect(self, room_id: str, player_id: str, ws: WebSocket):
        await ws.accept()
        if room_id not in self._connections:
            self._connections[room_id] = {}
        self._connections[room_id][player_id] = ws

    def disconnect(self, room_id: str, player_id: str):
        if room_id in self._connections:
            self._connections[room_id].pop(player_id, None)

    async def broadcast(self, room_id: str, sender_id: str, message: str):
        if room_id not in self._connections:
            return
        for pid, ws in self._connections[room_id].items():
            await ws.send_text(f'{{"sender":"{sender_id}","text":"{message}"}}')

    def room_exists(self, room_id: str) -> bool:
        return room_id in self._connections


ws_manager = WSManager()
