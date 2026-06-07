"""Character management — core admin module."""
from fastapi import APIRouter, HTTPException
from ..services.store import store

router = APIRouter(prefix="/api/admin/characters", tags=["characters"])

@router.post("", status_code=201)
def create_character(data: dict):
    if "script_id" not in data or "name" not in data:
        raise HTTPException(400, "script_id and name required")
    c = store.create_character(data)
    return c.__dict__

@router.get("")
def list_characters(script_id: str | None = None):
    return store.list_characters(script_id)

@router.get("/{character_id}")
def get_character(character_id: str):
    c = store.get_character(character_id)
    if not c: raise HTTPException(404, "Character not found")
    return c.__dict__

@router.put("/{character_id}")
def update_character(character_id: str, data: dict):
    c = store.update_character(character_id, data)
    if not c: raise HTTPException(404, "Character not found")
    return c.__dict__

@router.delete("/{character_id}")
def delete_character(character_id: str):
    if not store.delete_character(character_id):
        raise HTTPException(404, "Character not found")
    return {"status": "deleted"}

@router.post("/{character_id}/validate")
def validate_character(character_id: str):
    c = store.get_character(character_id)
    if not c: raise HTTPException(404, "Character not found")
    warnings = []
    if c.is_killer and not c.lie_topics:
        warnings.append("凶手未配置谎言辐射范围")
    for k in c.knowledge:
        if k.get("level") in ("L2","L3","L4") and not k.get("time_label"):
            warnings.append(f"知识条目缺少时间标签: {k.get('content','')[:30]}")
    return {"character_id": character_id, "warnings": warnings}
