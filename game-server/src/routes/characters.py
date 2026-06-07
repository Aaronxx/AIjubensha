"""Character management routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from ..models.character import (
    CharacterCreate, CharacterUpdate, CharacterScriptAssignment,
    PersonalityMatrix, KnowledgeEntry, ArcState, ArcTransition,
    SilenceStrategy, CharacterType
)
from ..services.character_service import character_service

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_character(char_data: CharacterCreate):
    """Create a new NPC character."""
    result = await character_service.create_character(char_data)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.get("", response_model=dict)
async def list_characters(
    search: Optional[str] = Query(None, description="Search in name/background"),
    occupation: Optional[str] = Query(None, description="Filter by occupation"),
    sort_by: str = Query("created_at", pattern="^(name|created_at|usage_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List characters with filtering."""
    return await character_service.list_characters(
        search=search,
        occupation=occupation,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )


@router.get("/{char_id}", response_model=dict)
async def get_character(char_id: str, detail: bool = Query(False)):
    """Get character by ID."""
    if detail:
        char = await character_service.get_character_detail(char_id)
    else:
        char = await character_service.get_character(char_id)

    if not char:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    return char


@router.patch("/{char_id}", response_model=dict)
async def update_character(char_id: str, update_data: CharacterUpdate):
    """Update a character."""
    result = await character_service.update_character(char_id, update_data)

    if not result["success"]:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in result["error"] else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result


@router.delete("/{char_id}", response_model=dict)
async def delete_character(char_id: str):
    """Delete a character."""
    result = await character_service.delete_character(char_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )

    return result


@router.post("/{char_id}/scripts", response_model=dict)
async def assign_to_script(char_id: str, assignment: CharacterScriptAssignment):
    """Assign character to a script."""
    result = await character_service.assign_to_script(char_id, assignment)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in result["error"] else status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


@router.delete("/{char_id}/scripts/{script_id}", response_model=dict)
async def remove_from_script(char_id: str, script_id: str):
    """Remove character from a script."""
    result = await character_service.remove_from_script(char_id, script_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )

    return result


@router.get("/scripts/{script_id}", response_model=list)
async def get_characters_for_script(script_id: str):
    """Get all characters assigned to a script."""
    return await character_service.get_characters_for_script(script_id)


@router.get("/types", response_model=list)
async def get_character_types():
    """Get available character self-awareness types."""
    return [
        {"value": CharacterType.OMNISCIENT.value, "label": "全知型", "description": "亲手作案，未失忆，推理环节辩解/误导"},
        {"value": CharacterType.PROGRESSIVE.value, "label": "渐进发现型", "description": "失忆设定，逐步发现自己可能是凶手"},
        {"value": CharacterType.UNAWARE.value, "label": "全程不知型", "description": "被利用/间接作案，和其他人一起推理"},
        {"value": CharacterType.ACCOMPLICE.value, "label": "多人共犯型", "description": "东方快车式，多人参与，不知谁致命"},
        {"value": CharacterType.SCAPEGOAT.value, "label": "替罪羊型", "description": "被陷害，需要自证清白"}
    ]


@router.get("/silence-strategies", response_model=list)
async def get_silence_strategies():
    """Get available silence/avoidance strategies."""
    return [
        {"value": SilenceStrategy.HARD_SILENCE.value, "label": "硬沉默"},
        {"value": SilenceStrategy.POLITE_REFUSAL.value, "label": "委婉拒绝"},
        {"value": SilenceStrategy.TOPIC_SHIFT.value, "label": "转移话题"},
        {"value": SilenceStrategy.EVASION.value, "label": "顾左右而言他"},
        {"value": SilenceStrategy.EMOTIONAL.value, "label": "情绪回避"}
    ]
