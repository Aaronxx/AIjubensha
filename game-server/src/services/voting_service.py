"""Voting system service."""
from datetime import datetime, timezone
from typing import Optional, List, Dict
from uuid import uuid4
from collections import Counter

from ..models.voting import (
    Vote, VoteSession, VoteType, VoteResult,
    DetectiveVoteRequest, FinalVoteRequest,
    TieBreakerSession, TieBreakerVote, VoteRevealSequence
)


class VotingService:
    """Manages voting system operations."""

    def __init__(self):
        # In-memory stores
        self._vote_sessions: dict[str, VoteSession] = {}
        self._tie_breakers: dict[str, TieBreakerSession] = {}
        self._player_votes: dict[str, List[str]] = {}  # player_id -> list of vote_session_ids

    async def create_vote_session(
        self,
        game_session_id: str,
        vote_type: VoteType,
        eligible_voters: List[str]
    ) -> VoteSession:
        """Create a new voting session."""
        session_id = str(uuid4())

        session = VoteSession(
            session_id=session_id,
            game_session_id=game_session_id,
            vote_type=vote_type,
            status="waiting",
            voter_count=len(eligible_voters),
            voted_count=0,
            votes=[]
        )

        self._vote_sessions[session_id] = session
        return session

    async def start_voting(self, session_id: str) -> VoteSession:
        """Start voting session."""
        if session_id not in self._vote_sessions:
            raise ValueError(f"Vote session {session_id} not found")

        session = self._vote_sessions[session_id]
        session.status = "active"
        session.start_time = datetime.now(timezone.utc)

        return session

    async def cast_vote(
        self,
        session_id: str,
        voter_id: str,
        voter_name: str,
        target_id: str,
        target_name: str
    ) -> Vote:
        """Cast a vote."""
        if session_id not in self._vote_sessions:
            raise ValueError(f"Vote session {session_id} not found")

        session = self._vote_sessions[session_id]

        if session.status != "active":
            raise ValueError("Voting is not active")

        # Check if already voted
        existing = next((v for v in session.votes if v.voter_id == voter_id), None)
        if existing:
            raise ValueError("Already voted")

        vote = Vote(
            vote_id=str(uuid4()),
            session_id=session_id,
            voter_id=voter_id,
            voter_name=voter_name,
            target_id=target_id,
            target_name=target_name,
            vote_type=session.vote_type,
            timestamp=datetime.now(timezone.utc),
            is_valid=True
        )

        session.votes.append(vote)
        session.voted_count = len(session.votes)

        # Track player votes
        if voter_id not in self._player_votes:
            self._player_votes[voter_id] = []
        self._player_votes[voter_id].append(session_id)

        return vote

    async def calculate_results(self, session_id: str) -> VoteResult:
        """Calculate vote results."""
        if session_id not in self._vote_sessions:
            return VoteResult(
                success=False,
                vote_type=VoteType.FINAL,
                total_votes=0,
                results={},
                message="Session not found"
            )

        session = self._vote_sessions[session_id]

        # Count votes
        vote_counts = Counter(v.target_id for v in session.votes)
        results = dict(vote_counts)

        total_votes = len(session.votes)

        # Find winner
        winner = None
        winner_votes = 0
        is_tie = False
        tie_players = []

        if results:
            max_votes = max(results.values())
            winners = [k for k, v in results.items() if v == max_votes]

            if len(winners) == 1:
                winner = winners[0]
                winner_votes = max_votes
            else:
                is_tie = True
                tie_players = winners
                winner_votes = max_votes

        return VoteResult(
            success=True,
            vote_type=session.vote_type,
            total_votes=total_votes,
            results=results,
            winner=winner,
            winner_votes=winner_votes,
            is_tie=is_tie,
            tie_players=tie_players
        )

    async def end_voting(self, session_id: str) -> VoteSession:
        """End voting session."""
        if session_id not in self._vote_sessions:
            raise ValueError(f"Vote session {session_id} not found")

        session = self._vote_sessions[session_id]
        session.status = "finished"
        session.end_time = datetime.now(timezone.utc)

        # Calculate final results
        result = await self.calculate_results(session_id)
        session.result = result.model_dump()

        return session

    async def start_tie_breaker(
        self,
        original_session_id: str,
        tied_players: List[str]
    ) -> TieBreakerSession:
        """Start a tie breaker session."""
        if original_session_id not in self._vote_sessions:
            raise ValueError("Original session not found")

        tie_session = TieBreakerSession(
            original_session_id=original_session_id,
            tied_players=tied_players,
            status="active"
        )

        self._tie_breakers[original_session_id] = tie_session
        return tie_session

    async def cast_tie_breaker_vote(
        self,
        original_session_id: str,
        voter_id: str,
        target_id: str
    ) -> TieBreakerVote:
        """Cast a tie breaker vote."""
        if original_session_id not in self._tie_breakers:
            raise ValueError("Tie breaker session not found")

        tie_session = self._tie_breakers[original_session_id]

        if tie_session.status != "active":
            raise ValueError("Tie breaker is not active")

        if target_id not in tie_session.tied_players:
            raise ValueError("Can only vote for tied players")

        vote = TieBreakerVote(
            voter_id=voter_id,
            target_id=target_id,
            timestamp=datetime.now(timezone.utc)
        )

        tie_session.votes.append(vote)

        # Check if we have enough votes to break tie
        # Simplified: first to get majority wins
        vote_counts = Counter(v.target_id for v in tie_session.votes)
        total_votes = len(tie_session.votes)

        for player, count in vote_counts.items():
            if count > total_votes / 2:
                tie_session.result = player
                tie_session.status = "finished"
                break

        return vote

    async def get_vote_session(self, session_id: str) -> Optional[VoteSession]:
        """Get vote session by ID."""
        return self._vote_sessions.get(session_id)

    async def has_voted(self, session_id: str, voter_id: str) -> bool:
        """Check if a player has voted."""
        if session_id not in self._vote_sessions:
            return False

        session = self._vote_sessions[session_id]
        return any(v.voter_id == voter_id for v in session.votes)

    async def get_player_vote_history(self, player_id: str) -> List[Dict]:
        """Get player's vote history."""
        if player_id not in self._player_votes:
            return []

        history = []
        for session_id in self._player_votes[player_id]:
            session = self._vote_sessions.get(session_id)
            if session:
                vote = next((v for v in session.votes if v.voter_id == player_id), None)
                if vote:
                    history.append({
                        "session_id": session_id,
                        "vote_type": session.vote_type.value,
                        "voted_for": vote.target_name,
                        "timestamp": vote.timestamp.isoformat()
                    })

        return history

    async def prepare_reveal_sequence(
        self,
        session_id: str,
        players: List[Dict]
    ) -> VoteRevealSequence:
        """Prepare vote reveal sequence."""
        result = await self.calculate_results(session_id)

        # Categorize players by vote count
        zero_vote = []
        low_vote = []
        high_vote = []

        # Create player ID to name mapping
        player_map = {p["id"]: p["name"] for p in players}

        # Get all player IDs
        all_players = set(player_map.keys())
        voted_players = set(result.results.keys())

        # 0 votes
        zero_vote = [player_map.get(pid, pid) for pid in all_players - voted_players]

        # 1-2 votes
        low_vote = [
            player_map.get(pid, pid)
            for pid, count in result.results.items()
            if 1 <= count <= 2
        ]

        # High votes (tie or winner)
        if result.is_tie:
            high_vote = [player_map.get(pid, pid) for pid in result.tie_players]
        elif result.winner:
            high_vote = [player_map.get(result.winner, result.winner)]

        return VoteRevealSequence(
            zero_vote_players=zero_vote,
            low_vote_players=low_vote,
            high_vote_players=high_vote,
            final_result="tie" if result.is_tie else result.winner
        )


# Singleton instance
voting_service = VotingService()
