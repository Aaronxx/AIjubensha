"""Investigation (搜证) system routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from ..services.game_service import game_manager

router = APIRouter()


class InvestigateRequest(BaseModel):
    player_id: str
    target_id: str
    ap_cost: int


class RevealClueRequest(BaseModel):
    player_id: str
    clue_id: str
    is_public: bool = True


@router.get("/game/{room_id}/investigation")
async def get_investigation_state(room_id: str, player_id: str):
    """Get current investigation state for a player."""
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    player = session.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return {
        "ap_remaining": player.ap_remaining,
        "clues_discovered": player.clues_discovered,
        "clues_public": player.clues_public,
        "current_phase": session.current_phase.value,
    }


@router.post("/game/{room_id}/investigation/investigate")
async def investigate(room_id: str, req: InvestigateRequest):
    """Player spends AP to investigate a target."""
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    player = session.get_player(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Check phase
    if session.current_phase.value not in ["round_1_search", "round_2_search"]:
        raise HTTPException(status_code=400, detail="Not in investigation phase")

    # Check AP
    if player.ap_remaining < req.ap_cost:
        raise HTTPException(status_code=400, detail="Insufficient AP")

    # Deduct AP
    player.ap_remaining -= req.ap_cost

    # Generate clue (simplified - in real implementation, this would query the script data)
    clue_id = f"clue_{req.target_id}_{req.ap_cost}"
    if clue_id not in player.clues_discovered:
        player.clues_discovered.append(clue_id)

    return {
        "ap_remaining": player.ap_remaining,
        "clue_discovered": clue_id,
        "target_id": req.target_id,
    }


@router.post("/game/{room_id}/investigation/reveal")
async def reveal_clue(room_id: str, req: RevealClueRequest):
    """Player reveals a clue to public or keeps it private."""
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    player = session.get_player(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if req.clue_id not in player.clues_discovered:
        raise HTTPException(status_code=400, detail="Clue not discovered")

    if req.is_public:
        if req.clue_id not in player.clues_public:
            player.clues_public.append(req.clue_id)

    return {
        "clue_id": req.clue_id,
        "is_public": req.is_public,
        "public_clues": player.clues_public,
    }


@router.get("/game/{room_id}/clues")
async def get_public_clues(room_id: str):
    """Get all publicly revealed clues in the game."""
    session = game_manager.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    public_clues = {}
    for player_id, player in session.players.items():
        public_clues[player_id] = player.clues_public

    return {"public_clues": public_clues}
