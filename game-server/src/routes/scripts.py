"""Script management routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from ..models.script import ScriptCreate, ScriptUpdate, DifficultyLevel, ScriptType
from ..services.script_service import script_service
from ..services.auth_service import auth_service

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_script(script_data: ScriptCreate):
    """Create a new script."""
    result = await script_service.create_script(script_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.get("", response_model=list)
async def list_scripts(
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    script_type: Optional[ScriptType] = Query(None, description="Filter by type"),
    min_players: Optional[int] = Query(None, ge=4, le=8, description="Minimum players"),
    max_players: Optional[int] = Query(None, ge=4, le=8, description="Maximum players"),
    search: Optional[str] = Query(None, description="Search in title/description/tags"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating|play_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List scripts with filtering and pagination."""
    scripts = await script_service.list_scripts(
        difficulty=difficulty,
        script_type=script_type,
        min_players=min_players,
        max_players=max_players,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return scripts


@router.get("/{script_id}", response_model=dict)
async def get_script(script_id: str):
    """Get script by ID."""
    script = await script_service.get_script(script_id)

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found"
        )

    return script


@router.patch("/{script_id}", response_model=dict)
async def update_script(script_id: str, update_data: ScriptUpdate):
    """Update a script."""
    result = await script_service.update_script(script_id, update_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if result["error"] == "Script not found"
            else status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.delete("/{script_id}", response_model=dict)
async def delete_script(script_id: str):
    """Delete a script."""
    result = await script_service.delete_script(script_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )

    return result


@router.post("/{script_id}/rate")
async def rate_script(script_id: str, rating: float = Query(..., ge=0, le=5)):
    """Rate a script."""
    success = await script_service.rate_script(script_id, rating)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found"
        )

    return {"success": True}


@router.get("/types", response_model=list)
async def get_script_types():
    """Get available script types."""
    return [
        {"value": ScriptType.BENGGE.value, "label": "本格推理", "description": "逻辑严密的谜题"},
        {"value": ScriptType.SOCIAL.value, "label": "社交博弈", "description": "复杂的人物关系"},
        {"value": ScriptType.EMOTIONAL.value, "label": "情感沉浸", "description": "情绪驱动叙事"}
    ]


@router.get("/difficulties", response_model=list)
async def get_difficulties():
    """Get available difficulty levels."""
    return [
        {"value": DifficultyLevel.EASY.value, "label": "入门", "description": "60分钟，线索明显"},
        {"value": DifficultyLevel.STANDARD.value, "label": "标准", "description": "75分钟，正常推理"},
        {"value": DifficultyLevel.HARD.value, "label": "硬核", "description": "90分钟，复杂谜题"}
    ]
