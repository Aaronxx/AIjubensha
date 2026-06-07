"""End-to-end integration test: full game flow."""
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
    sid = "script_01"
    script = ScriptInDB(
        id=sid,
        title="山庄晚宴",
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
    script_service._title_index["山庄晚宴"] = sid

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


class TestFullGameFlow:
    def test_complete_game_from_creation_to_finish(self, client):
        """Simulate a complete 4-player game through all 9 phases."""
        # ── Create room ──
        r = client.post("/api/rooms", json={
            "script_id": "script_01", "name": "山庄晚宴", "max_players": 4,
            "host_id": "test_user", "host_username": "test_user"
        })
        assert r.status_code == 201, r.text
        room_id = r.json()["room_id"]

        # ── Join players ──
        players = [
            ("alice", "char_su", "normal"),
            ("bob", "char_chen", "detective"),
            ("charlie", "char_zhou", "killer"),
            ("diana", "char_lin", "normal"),
        ]
        for pid, cid, role in players:
            resp = client.post(f"/api/rooms/{room_id}/join", json={
                "player_id": pid, "character_id": cid, "role": role,
            })
            assert resp.status_code == 200, resp.text

        # ── Phase 0: Preparation → all confirm ──
        for pid, _, _ in players:
            resp = client.post(f"/api/game/{room_id}/confirm", json={"player_id": pid})
            assert resp.status_code == 200, resp.text
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "act_1_turn"

        # ── Phase 1: Act 1 ──
        resp = client.post(f"/api/game/{room_id}/force-advance")  # skip turn talk → free exchange
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "round_1_search"

        # ── Phase 2: Round 1 Search ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "act_2_discuss"

        # ── Phase 3: Act 2 Discussion ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "detective_vote"

        # ── Phase 4: Detective solo vote ──
        resp = client.post(f"/api/game/{room_id}/vote", json={
            "voter_id": "bob", "target_id": "charlie",
        })
        assert resp.status_code == 200, resp.text
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "round_2_search"

        # ── Phase 5: Round 2 Search ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "act_3_discuss"

        # ── Phase 6: Act 3 Discussion ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "final_vote"

        # ── Phase 7: Final vote ──
        votes = [("alice", "charlie"), ("bob", "charlie"), ("diana", "charlie"), ("charlie", "alice")]
        for voter, target in votes:
            resp = client.post(f"/api/game/{room_id}/vote", json={
                "voter_id": voter, "target_id": target,
            })
            assert resp.status_code == 200, resp.text

        # ── Phase 8: Result ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "result"

        # ── Phase 9: Finished ──
        resp = client.post(f"/api/game/{room_id}/force-advance")
        state = client.get(f"/api/game/{room_id}").json()
        assert state["current_phase"] == "finished"
