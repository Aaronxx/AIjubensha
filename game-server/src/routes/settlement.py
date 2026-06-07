"""Settlement and achievement routes."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models.settlement import (
    SettlementRequest, SettlementSummary,
    PlayerStats, Achievement, AchievementRarity,
    PlayerRankEntry
)
from ..services.settlement_service import settlement_service

router = APIRouter(prefix="/settlement", tags=["settlement"])


@router.post("/settle", response_model=SettlementSummary)
async def settle_game(
    request: SettlementRequest,
    player_data: List[dict]
):
    """Settle a game and generate records."""
    summary = await settlement_service.settle_game(request, player_data)
    return summary


@router.get("/games/{game_session_id}/summary", response_model=SettlementSummary)
async def get_settlement_summary(game_session_id: str):
    """Get settlement summary for a game."""
    summary = await settlement_service.get_settlement_summary(game_session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Settlement not found")
    return summary


@router.get("/players/{player_id}/stats", response_model=Optional[PlayerStats])
async def get_player_stats(player_id: str):
    """Get player statistics."""
    stats = await settlement_service.get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player stats not found")
    return stats


@router.get("/players/{player_id}/settlements")
async def get_player_settlements(
    player_id: str,
    limit: int = 20,
    offset: int = 0
):
    """Get player's settlement records."""
    settlements = await settlement_service.get_player_settlements(
        player_id=player_id,
        limit=limit,
        offset=offset
    )
    return settlements


@router.post("/achievements", response_model=Achievement)
async def create_achievement(achievement: Achievement):
    """Create a new achievement."""
    return await settlement_service.create_achievement(achievement)


@router.get("/achievements")
async def get_achievements(
    rarity: Optional[AchievementRarity] = None
):
    """Get all achievements."""
    achievements = await settlement_service.get_achievements(rarity)
    return {"achievements": achievements}


@router.get("/players/{player_id}/achievements")
async def get_player_achievements(player_id: str):
    """Get player's unlocked achievements."""
    achievements = await settlement_service.get_player_achievements(player_id)
    return achievements


@router.post("/players/{player_id}/check-achievements")
async def check_achievements(player_id: str):
    """Check and unlock achievements for a player."""
    unlocked = await settlement_service.check_achievements(player_id)
    return {
        "player_id": player_id,
        "newly_unlocked": unlocked,
        "count": len(unlocked)
    }


@router.get("/leaderboard")
async def get_leaderboard(
    category: str = "overall",
    limit: int = 100
):
    """Get leaderboard."""
    entries = await settlement_service.get_leaderboard(category, limit)
    return {
        "category": category,
        "entries": entries,
        "total": len(entries)
    }
