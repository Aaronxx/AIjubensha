"""Voting system routes."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models.voting import (
    VoteSession, Vote, VoteResult, VoteRevealSequence,
    DetectiveVoteRequest, FinalVoteRequest, VoteType
)
from ..services.voting_service import voting_service

router = APIRouter(prefix="/votes", tags=["voting"])


@router.post("/sessions", response_model=VoteSession)
async def create_vote_session(
    game_session_id: str,
    vote_type: VoteType,
    eligible_voters: List[str]
):
    """Create a new voting session."""
    session = await voting_service.create_vote_session(
        game_session_id=game_session_id,
        vote_type=vote_type,
        eligible_voters=eligible_voters
    )
    return session


@router.post("/sessions/{session_id}/start", response_model=VoteSession)
async def start_voting(session_id: str):
    """Start voting session."""
    try:
        session = await voting_service.start_voting(session_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/vote", response_model=Vote)
async def cast_vote(
    session_id: str,
    voter_id: str,
    voter_name: str,
    target_id: str,
    target_name: str
):
    """Cast a vote."""
    try:
        vote = await voting_service.cast_vote(
            session_id=session_id,
            voter_id=voter_id,
            voter_name=voter_name,
            target_id=target_id,
            target_name=target_name
        )
        return vote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/end", response_model=VoteSession)
async def end_voting(session_id: str):
    """End voting session and calculate results."""
    try:
        session = await voting_service.end_voting(session_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions/{session_id}/results", response_model=VoteResult)
async def get_vote_results(session_id: str):
    """Get vote results."""
    result = await voting_service.calculate_results(session_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return result


@router.post("/sessions/{session_id}/tie-breaker")
async def start_tie_breaker(
    session_id: str,
    tied_players: List[str]
):
    """Start a tie breaker session."""
    try:
        tie_session = await voting_service.start_tie_breaker(
            original_session_id=session_id,
            tied_players=tied_players
        )
        return tie_session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/tie-breaker/vote")
async def cast_tie_breaker_vote(
    session_id: str,
    voter_id: str,
    target_id: str
):
    """Cast a tie breaker vote."""
    try:
        vote = await voting_service.cast_tie_breaker_vote(
            original_session_id=session_id,
            voter_id=voter_id,
            target_id=target_id
        )
        return vote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/reveal", response_model=VoteRevealSequence)
async def prepare_reveal_sequence(
    session_id: str,
    players: List[dict]
):
    """Prepare vote reveal sequence."""
    sequence = await voting_service.prepare_reveal_sequence(
        session_id=session_id,
        players=players
    )
    return sequence


@router.get("/sessions/{session_id}", response_model=Optional[VoteSession])
async def get_vote_session(session_id: str):
    """Get vote session by ID."""
    session = await voting_service.get_vote_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Vote session not found")
    return session


@router.get("/sessions/{session_id}/has-voted")
async def has_voted(session_id: str, voter_id: str):
    """Check if a player has voted."""
    voted = await voting_service.has_voted(session_id, voter_id)
    return {"voted": voted}


@router.get("/players/{player_id}/history")
async def get_player_vote_history(player_id: str):
    """Get player's vote history."""
    history = await voting_service.get_player_vote_history(player_id)
    return {"player_id": player_id, "history": history}
