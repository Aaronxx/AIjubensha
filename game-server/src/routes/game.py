"""Game session routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.game_service import game_manager

router = APIRouter()


class ConfirmRequest(BaseModel):
    player_id: str


class VoteRequest(BaseModel):
    voter_id: str
    target_id: str


@router.get("/game/{room_id}")
async def get_game_state(room_id: str):
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    return {
        "room_id": room_id,
        "current_phase": session.current_phase.value,
        "player_count": len(session.players),
        "is_free_exchange": session.is_free_exchange,
    }


@router.post("/game/{room_id}/confirm")
async def player_confirm(room_id: str, req: ConfirmRequest):
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    session.player_confirm(req.player_id)
    return {"status": "ok", "current_phase": session.current_phase.value}


@router.post("/game/{room_id}/force-advance")
async def force_advance(room_id: str):
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    session.force_phase_advance()
    return {"current_phase": session.current_phase.value}


@router.post("/game/{room_id}/vote")
async def cast_vote(room_id: str, req: VoteRequest):
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    session.cast_vote(req.voter_id, req.target_id)
    return {"status": "ok"}
