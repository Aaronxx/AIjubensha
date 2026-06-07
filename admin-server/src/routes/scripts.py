"""Script management routes."""
from fastapi import APIRouter, HTTPException
from ..services.store import store

router = APIRouter(prefix="/api/admin/scripts", tags=["scripts"])

@router.post("", status_code=201)
def create_script(data: dict):
    if "name" not in data: raise HTTPException(400, "name required")
    s = store.create_script(data)
    return s.__dict__

@router.get("")
def list_scripts(): return store.list_scripts()

@router.get("/{script_id}")
def get_script(script_id: str):
    s = store.get_script(script_id)
    if not s: raise HTTPException(404, "Script not found")
    return s.__dict__

@router.put("/{script_id}")
def update_script(script_id: str, data: dict):
    s = store.update_script(script_id, data)
    if not s: raise HTTPException(404)
    return s.__dict__

@router.delete("/{script_id}")
def delete_script(script_id: str):
    if not store.delete_script(script_id): raise HTTPException(404)
    return {"status": "deleted"}

@router.get("/{script_id}/characters")
def script_characters(script_id: str):
    return store.list_characters(script_id)

@router.post("/{script_id}/export")
def export_script(script_id: str):
    s = store.get_script(script_id)
    if not s: raise HTTPException(404)
    chars = store.list_characters(script_id)
    return {"script": s.__dict__, "characters": chars}
