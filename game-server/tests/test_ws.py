"""TDD: WebSocket group chat."""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.routes.rooms import get_current_user
from src.services.script_service import script_service


@pytest.fixture(autouse=True)
def seed_test_scripts():
    """Seed test scripts and clear service state before each test."""
    from src.services.room_service import room_service
    from src.services.game_service import game_manager

    script_service._scripts.clear()
    script_service._title_index.clear()
    room_service._rooms.clear()
    room_service._user_rooms.clear()
    game_manager._sessions.clear()

    from datetime import datetime, timezone
    from src.models.script import ScriptInDB, DifficultyLevel, ScriptType

    now = datetime.now(timezone.utc)
    sid = "ws_test_script"
    script = ScriptInDB(
        id=sid,
        title="WS Test Script",
        description="A test script",
        script_type=ScriptType.BENGGE,
        difficulty=DifficultyLevel.EASY,
        min_players=4,
        max_players=4,
        duration_minutes=75,
        created_at=now,
        updated_at=now,
        play_count=0,
        rating=0.0,
        rating_count=0,
        is_published=True,
    )
    script_service._scripts[sid] = script
    script_service._title_index["WS Test Script"] = sid

    yield


@pytest.fixture
def client():
    """Test client with auth dependency overridden."""
    async def mock_user():
        return {"user_id": "test_user", "username": "test_user"}

    app.dependency_overrides[get_current_user] = mock_user

    c = TestClient(app)
    yield c

    app.dependency_overrides.clear()


class TestWebSocketChat:
    def test_ws_connect(self, client):
        """WebSocket connection succeeds for existing room."""
        r = client.post("/api/rooms", json={
            "script_id": "ws_test_script", "name": "WS Room", "max_players": 4,
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        client.post(f"/api/rooms/{room_id}/join", json={
            "player_id": "u1", "character_id": "c1", "role": "normal",
        })

        with client.websocket_connect(f"/ws/{room_id}?player_id=u1") as ws:
            assert ws is not None

    def test_ws_send_and_receive(self, client):
        """Messages are broadcast to room participants."""
        r = client.post("/api/rooms", json={
            "script_id": "ws_test_script", "name": "WS Room", "max_players": 4,
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        for pid, cid in [("u1","c1"),("u2","c2")]:
            client.post(f"/api/rooms/{room_id}/join", json={
                "player_id": pid, "character_id": cid, "role": "normal",
            })

        with client.websocket_connect(f"/ws/{room_id}?player_id=u1") as ws1:
            with client.websocket_connect(f"/ws/{room_id}?player_id=u2") as ws2:
                ws1.send_text("Hello from u1")
                data = ws2.receive_text()
                assert "u1" in data

    def test_ws_nonexistent_room(self, client):
        """WebSocket to nonexistent room returns error."""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/nonexistent?player_id=u1"):
                pass
