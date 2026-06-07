"""WebSocket chat routes."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..services.ws_manager import ws_manager
from ..services.game_service import game_manager

router = APIRouter()


@router.websocket("/ws/{room_id}")
async def chat_websocket(room_id: str, ws: WebSocket, player_id: str = Query(...)):
    # Verify room/game exists
    if not game_manager.get_session(room_id):
        await ws.close(code=4004, reason="Game not found")
        return

    await ws_manager.connect(room_id, player_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            await ws_manager.broadcast(room_id, player_id, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(room_id, player_id)
