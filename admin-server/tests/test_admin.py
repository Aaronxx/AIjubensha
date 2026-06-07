"""TDD: Admin backend — characters, scripts, achievements, shop, orders, users, audit."""
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestCharacterCRUD:
    def test_create_character(self, client):
        resp = client.post("/api/admin/characters", json={
            "script_id": "s1", "name": "苏晚晴", "age": 30, "occupation": "画廊老板",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "苏晚晴"

    def test_get_character(self, client):
        r = client.post("/api/admin/characters", json={"script_id": "s1", "name": "测试"})
        cid = r.json()["character_id"]
        resp = client.get(f"/api/admin/characters/{cid}")
        assert resp.status_code == 200

    def test_update_character(self, client):
        r = client.post("/api/admin/characters", json={"script_id": "s1", "name": "旧名"})
        cid = r.json()["character_id"]
        resp = client.put(f"/api/admin/characters/{cid}", json={"name": "新名"})
        assert resp.json()["name"] == "新名"

    def test_delete_character(self, client):
        r = client.post("/api/admin/characters", json={"script_id": "s1", "name": "待删"})
        cid = r.json()["character_id"]
        resp = client.delete(f"/api/admin/characters/{cid}")
        assert resp.status_code == 200

    def test_list_by_script(self, client):
        client.post("/api/admin/characters", json={"script_id": "s99", "name": "A"})
        client.post("/api/admin/characters", json={"script_id": "s99", "name": "B"})
        resp = client.get("/api/admin/characters?script_id=s99")
        assert len(resp.json()) == 2

    def test_validate_killer_missing_lie(self, client):
        r = client.post("/api/admin/characters", json={
            "script_id": "s1", "name": "凶手", "is_killer": True,
        })
        cid = r.json()["character_id"]
        resp = client.post(f"/api/admin/characters/{cid}/validate")
        assert len(resp.json()["warnings"]) >= 1  # Should warn about missing lie topics

    def test_not_found(self, client):
        resp = client.get("/api/admin/characters/nonexistent")
        assert resp.status_code == 404


class TestScriptCRUD:
    def test_create_script(self, client):
        resp = client.post("/api/admin/scripts", json={"name": "山庄晚宴"})
        assert resp.status_code == 201

    def test_list_scripts(self, client):
        client.post("/api/admin/scripts", json={"name": "A"})
        client.post("/api/admin/scripts", json={"name": "B"})
        resp = client.get("/api/admin/scripts")
        assert len(resp.json()) >= 2

    def test_script_characters(self, client):
        r = client.post("/api/admin/scripts", json={"name": "测试剧本"})
        sid = r.json()["script_id"]
        client.post("/api/admin/characters", json={"script_id": sid, "name": "C1"})
        resp = client.get(f"/api/admin/scripts/{sid}/characters")
        assert len(resp.json()) == 1

    def test_export(self, client):
        r = client.post("/api/admin/scripts", json={"name": "可导出"})
        sid = r.json()["script_id"]
        resp = client.post(f"/api/admin/scripts/{sid}/export")
        assert "script" in resp.json()
        assert "characters" in resp.json()


class TestAchievements:
    def test_crud(self, client):
        r = client.post("/api/admin/achievements", json={"name":"神探","rarity":"史诗","reward":50})
        assert r.status_code == 201
        resp = client.get("/api/admin/achievements")
        assert len(resp.json()) >= 1


class TestProducts:
    def test_crud(self, client):
        r = client.post("/api/admin/products", json={"name":"暗夜主题","category":"skin","price":120})
        assert r.status_code == 201
        resp = client.get("/api/admin/products")
        assert len(resp.json()) >= 1


class TestUsers:
    def test_list_and_ban(self, client):
        store = __import__("src.services.store", fromlist=["store"]).store
        store.users["u1"] = {"id":"u1","name":"test","status":"active"}
        resp = client.get("/api/admin/users")
        assert len(resp.json()) >= 1
        resp = client.post("/api/admin/users/u1/ban")
        assert resp.json()["status"] == "banned"


class TestDashboard:
    def test_dashboard(self, client):
        resp = client.get("/api/admin/dashboard")
        assert resp.status_code == 200
        assert "total_scripts" in resp.json()
