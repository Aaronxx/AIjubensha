"""Integration tests for API routes with auth override."""
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

    # Clear all service state BEFORE test
    script_service._scripts.clear()
    script_service._title_index.clear()
    room_service._rooms.clear()
    room_service._user_rooms.clear()
    game_manager._sessions.clear()

    from datetime import datetime, timezone
    from src.models.script import ScriptInDB, DifficultyLevel, ScriptType

    now = datetime.now(timezone.utc)
    for sid, title in [("script_01", "Test Script 1"), ("s1", "Test Script S1"), ("s2", "Test Script S2")]:
        script = ScriptInDB(
            id=sid,
            title=title,
            description="A test script",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=75,
            created_at=now,
            updated_at=now,
            play_count=0,
            rating=0.0,
            rating_count=0,
            is_published=True,
        )
        script_service._scripts[sid] = script
        script_service._title_index[title] = sid

    yield

    # Clear all service state AFTER test (teardown)
    script_service._scripts.clear()
    script_service._title_index.clear()
    room_service._rooms.clear()
    room_service._user_rooms.clear()
    game_manager._sessions.clear()


@pytest.fixture
def client():
    """Test client with auth dependency overridden."""
    async def mock_user():
        return {"user_id": "test_user", "username": "test_user"}

    app.dependency_overrides[get_current_user] = mock_user

    c = TestClient(app)
    yield c

    app.dependency_overrides.clear()


class TestRoomRoutes:
    def test_create_room(self, client):
        resp = client.post("/api/rooms", json={
            "name": "test_room",
            "script_id": "script_01",
            "max_players": 6,
            "host_id": "test_user",
            "host_username": "test_user"
        })
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "room_id" in data

    def test_list_rooms(self, client):
        # Create one room (list API returns a list, not a dict)
        client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        resp = client.get("/api/rooms")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_join_room(self, client):
        r = client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        resp = client.post(f"/api/rooms/{room_id}/join", json={
            "player_id": "u1", "character_id": "c1", "role": "normal",
        })
        assert resp.status_code == 200, resp.text

    def test_room_not_found(self, client):
        resp = client.get("/api/rooms/nonexistent")
        assert resp.status_code == 404


class TestGameRoutes:
    def test_player_confirm(self, client):
        r = client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        client.post(f"/api/rooms/{room_id}/join", json={
            "player_id": "u1", "character_id": "c1", "role": "normal",
        })
        resp = client.post(f"/api/game/{room_id}/confirm", json={"player_id": "u1"})
        assert resp.status_code == 200, resp.text

    def test_get_game_state(self, client):
        r = client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        client.post(f"/api/rooms/{room_id}/join", json={
            "player_id": "u1", "character_id": "c1", "role": "normal",
        })
        resp = client.get(f"/api/game/{room_id}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "current_phase" in data

    def test_game_not_found(self, client):
        resp = client.get("/api/game/nonexistent")
        assert resp.status_code == 404

    def test_cast_vote(self, client):
        r = client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        for pid, cid in [("u1", "c1"), ("u2", "c2"), ("u3", "c3")]:
            client.post(f"/api/rooms/{room_id}/join", json={
                "player_id": pid, "character_id": cid, "role": "normal",
            })
        for _ in range(7):
            client.post(f"/api/game/{room_id}/force-advance")
        resp = client.post(f"/api/game/{room_id}/vote", json={
            "voter_id": "u1", "target_id": "u3",
        })
        assert resp.status_code == 200, resp.text

    def test_force_advance_admin(self, client):
        r = client.post("/api/rooms", json={
            "name": "R1", "script_id": "s1",
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]
        client.post(f"/api/rooms/{room_id}/join", json={
            "player_id": "u1", "character_id": "c1", "role": "normal",
        })
        resp = client.post(f"/api/game/{room_id}/force-advance")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "current_phase" in data
