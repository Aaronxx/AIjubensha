"""Voting system tests."""
import pytest
from datetime import datetime

from src.services.voting_service import VotingService
from src.models.voting import VoteType, VoteResult


@pytest.fixture
def voting_service():
    """Create a fresh voting service for tests."""
    service = VotingService()
    # Clear any existing data
    service._vote_sessions.clear()
    service._tie_breakers.clear()
    service._player_votes.clear()
    return service


class TestVoteSession:
    """Test voting session management."""

    @pytest.mark.asyncio
    async def test_create_vote_session(self, voting_service):
        """Test creating vote session."""
        session = await voting_service.create_vote_session(
            game_session_id="game_001",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002", "player_003"]
        )

        assert session.game_session_id == "game_001"
        assert session.vote_type == VoteType.FINAL
        assert session.status == "waiting"
        assert session.voter_count == 3
        assert session.voted_count == 0
        assert len(session.votes) == 0

    @pytest.mark.asyncio
    async def test_start_voting(self, voting_service):
        """Test starting voting session."""
        session = await voting_service.create_vote_session(
            game_session_id="game_002",
            vote_type=VoteType.DETECTIVE_MID,
            eligible_voters=["player_001", "player_002"]
        )

        started = await voting_service.start_voting(session.session_id)

        assert started.status == "active"
        assert started.start_time is not None

    @pytest.mark.asyncio
    async def test_start_voting_not_found(self, voting_service):
        """Test starting non-existent session."""
        with pytest.raises(ValueError, match="Vote session.*not found"):
            await voting_service.start_voting("invalid_session_id")


class TestCastVote:
    """Test voting mechanics."""

    @pytest.mark.asyncio
    async def test_cast_vote_success(self, voting_service):
        """Test successful vote casting."""
        # Setup
        session = await voting_service.create_vote_session(
            game_session_id="game_003",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002", "player_003"]
        )
        await voting_service.start_voting(session.session_id)

        # Cast vote
        vote = await voting_service.cast_vote(
            session_id=session.session_id,
            voter_id="player_001",
            voter_name="Alice",
            target_id="player_002",
            target_name="Bob"
        )

        assert vote.voter_id == "player_001"
        assert vote.target_id == "player_002"
        assert vote.vote_type == VoteType.FINAL
        assert vote.is_valid is True

        # Check session updated
        updated_session = await voting_service.get_vote_session(session.session_id)
        assert updated_session.voted_count == 1
        assert len(updated_session.votes) == 1

    @pytest.mark.asyncio
    async def test_cast_vote_session_not_found(self, voting_service):
        """Test voting in non-existent session."""
        with pytest.raises(ValueError, match="Vote session.*not found"):
            await voting_service.cast_vote(
                session_id="invalid_session",
                voter_id="player_001",
                voter_name="Alice",
                target_id="player_002",
                target_name="Bob"
            )

    @pytest.mark.asyncio
    async def test_cast_vote_not_active(self, voting_service):
        """Test voting when session not active."""
        session = await voting_service.create_vote_session(
            game_session_id="game_004",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001"]
        )
        # Don't start the session

        with pytest.raises(ValueError, match="Voting is not active"):
            await voting_service.cast_vote(
                session_id=session.session_id,
                voter_id="player_001",
                voter_name="Alice",
                target_id="player_002",
                target_name="Bob"
            )

    @pytest.mark.asyncio
    async def test_cast_vote_already_voted(self, voting_service):
        """Test duplicate vote prevention."""
        session = await voting_service.create_vote_session(
            game_session_id="game_005",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002"]
        )
        await voting_service.start_voting(session.session_id)

        # First vote
        await voting_service.cast_vote(
            session_id=session.session_id,
            voter_id="player_001",
            voter_name="Alice",
            target_id="player_002",
            target_name="Bob"
        )

        # Try to vote again
        with pytest.raises(ValueError, match="Already voted"):
            await voting_service.cast_vote(
                session_id=session.session_id,
                voter_id="player_001",
                voter_name="Alice",
                target_id="player_003",
                target_name="Charlie"
            )


class TestCalculateResults:
    """Test vote result calculation."""

    @pytest.mark.asyncio
    async def test_calculate_results_winner(self, voting_service):
        """Test result calculation with clear winner."""
        session = await voting_service.create_vote_session(
            game_session_id="game_006",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3", "p4"]
        )
        await voting_service.start_voting(session.session_id)

        # Cast votes: player_002 gets 3 votes
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p2", "B", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p3", "C", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p4", "D", "player_003", "Charlie")

        result = await voting_service.calculate_results(session.session_id)

        assert result.success is True
        assert result.total_votes == 4
        assert result.winner == "player_002"
        assert result.winner_votes == 3
        assert result.is_tie is False
        assert result.results["player_002"] == 3
        assert result.results["player_003"] == 1

    @pytest.mark.asyncio
    async def test_calculate_results_tie(self, voting_service):
        """Test result calculation with tie."""
        session = await voting_service.create_vote_session(
            game_session_id="game_007",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3", "p4"]
        )
        await voting_service.start_voting(session.session_id)

        # Cast votes: tie between player_002 and player_003
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p2", "B", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p3", "C", "player_003", "Charlie")
        await voting_service.cast_vote(session.session_id, "p4", "D", "player_003", "Charlie")

        result = await voting_service.calculate_results(session.session_id)

        assert result.success is True
        assert result.is_tie is True
        assert result.winner is None
        assert result.tie_players == ["player_002", "player_003"]
        assert result.winner_votes == 2

    @pytest.mark.asyncio
    async def test_calculate_results_session_not_found(self, voting_service):
        """Test result calculation for non-existent session."""
        result = await voting_service.calculate_results("invalid_session")

        assert result.success is False
        assert "Session not found" in result.message

    @pytest.mark.asyncio
    async def test_calculate_results_no_votes(self, voting_service):
        """Test result calculation with no votes."""
        session = await voting_service.create_vote_session(
            game_session_id="game_008",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2"]
        )

        result = await voting_service.calculate_results(session.session_id)

        assert result.success is True
        assert result.total_votes == 0
        assert result.winner is None
        assert result.is_tie is False


class TestEndVoting:
    """Test ending voting session."""

    @pytest.mark.asyncio
    async def test_end_voting(self, voting_service):
        """Test ending voting session."""
        session = await voting_service.create_vote_session(
            game_session_id="game_009",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3"]
        )
        await voting_service.start_voting(session.session_id)
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_002", "Bob")

        ended = await voting_service.end_voting(session.session_id)

        assert ended.status == "finished"
        assert ended.end_time is not None
        assert ended.result is not None
        assert ended.result["winner"] == "player_002"

    @pytest.mark.asyncio
    async def test_end_voting_not_found(self, voting_service):
        """Test ending non-existent session."""
        with pytest.raises(ValueError, match="Vote session.*not found"):
            await voting_service.end_voting("invalid_session")


class TestTieBreaker:
    """Test tie breaker functionality."""

    @pytest.mark.asyncio
    async def test_start_tie_breaker(self, voting_service):
        """Test starting tie breaker."""
        session = await voting_service.create_vote_session(
            game_session_id="game_010",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3", "p4"]
        )
        await voting_service.start_voting(session.session_id)

        # Create tie
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p2", "B", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p3", "C", "player_003", "Charlie")
        await voting_service.cast_vote(session.session_id, "p4", "D", "player_003", "Charlie")

        tie_session = await voting_service.start_tie_breaker(
            original_session_id=session.session_id,
            tied_players=["player_002", "player_003"]
        )

        assert tie_session.original_session_id == session.session_id
        assert tie_session.tied_players == ["player_002", "player_003"]
        assert tie_session.status == "active"

    @pytest.mark.asyncio
    async def test_cast_tie_breaker_vote(self, voting_service):
        """Test casting tie breaker vote."""
        session = await voting_service.create_vote_session(
            game_session_id="game_011",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3", "p4"]
        )
        await voting_service.start_voting(session.session_id)

        # Create tie and start tie breaker
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p2", "B", "player_003", "Charlie")
        await voting_service.cast_vote(session.session_id, "p3", "C", "player_002", "Bob")
        await voting_service.cast_vote(session.session_id, "p4", "D", "player_003", "Charlie")

        await voting_service.start_tie_breaker(
            original_session_id=session.session_id,
            tied_players=["player_002", "player_003"]
        )

        # Cast first tie breaker vote - gets majority immediately (1 > 0/2)
        await voting_service.cast_tie_breaker_vote(
            original_session_id=session.session_id,
            voter_id="tb1",
            target_id="player_002"
        )

        # Should be finished after first vote
        tie_session = voting_service._tie_breakers[session.session_id]
        assert tie_session.status == "finished"
        assert tie_session.result == "player_002"

        # Verify subsequent votes fail since tie breaker is finished
        with pytest.raises(ValueError, match="Tie breaker is not active"):
            await voting_service.cast_tie_breaker_vote(
                original_session_id=session.session_id,
                voter_id="tb2",
                target_id="player_003"
            )

    @pytest.mark.asyncio
    async def test_cast_tie_breaker_vote_invalid_target(self, voting_service):
        """Test voting for non-tied player."""
        session = await voting_service.create_vote_session(
            game_session_id="game_012",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2"]
        )
        await voting_service.start_voting(session.session_id)

        await voting_service.start_tie_breaker(
            original_session_id=session.session_id,
            tied_players=["player_002", "player_003"]
        )

        with pytest.raises(ValueError, match="Can only vote for tied players"):
            await voting_service.cast_tie_breaker_vote(
                original_session_id=session.session_id,
                voter_id="p1",
                target_id="player_004"  # Not in tied players
            )


class TestVoteReveal:
    """Test vote reveal sequence."""

    @pytest.mark.asyncio
    async def test_prepare_reveal_sequence(self, voting_service):
        """Test preparing reveal sequence."""
        session = await voting_service.create_vote_session(
            game_session_id="game_013",
            vote_type=VoteType.FINAL,
            eligible_voters=["p1", "p2", "p3", "p4", "p5", "p6"]
        )
        await voting_service.start_voting(session.session_id)

        # Cast votes with different counts
        # player_001: 0 votes
        # player_002: 1 vote (low)
        # player_003: 2 votes (low)
        # player_004: 3 votes (high/winner)
        await voting_service.cast_vote(session.session_id, "p1", "A", "player_004", "D")
        await voting_service.cast_vote(session.session_id, "p2", "B", "player_004", "D")
        await voting_service.cast_vote(session.session_id, "p3", "C", "player_004", "D")
        await voting_service.cast_vote(session.session_id, "p4", "D", "player_002", "B")
        await voting_service.cast_vote(session.session_id, "p5", "E", "player_003", "C")
        await voting_service.cast_vote(session.session_id, "p6", "F", "player_003", "C")

        players = [
            {"id": "player_001", "name": "Alice"},
            {"id": "player_002", "name": "Bob"},
            {"id": "player_003", "name": "Charlie"},
            {"id": "player_004", "name": "David"},
            {"id": "player_005", "name": "Eve"},
            {"id": "player_006", "name": "Frank"}
        ]

        sequence = await voting_service.prepare_reveal_sequence(
            session_id=session.session_id,
            players=players
        )

        assert "Alice" in sequence.zero_vote_players  # 0 votes
        assert "Bob" in sequence.low_vote_players     # 1 vote
        assert "Charlie" in sequence.low_vote_players # 2 votes
        assert "David" in sequence.high_vote_players  # 3 votes (winner)
        assert sequence.final_result == "player_004"


class TestVoteHistory:
    """Test vote history tracking."""

    @pytest.mark.asyncio
    async def test_get_player_vote_history(self, voting_service):
        """Test retrieving player vote history."""
        session1 = await voting_service.create_vote_session(
            game_session_id="game_014",
            vote_type=VoteType.DETECTIVE_MID,
            eligible_voters=["player_001", "player_002"]
        )
        await voting_service.start_voting(session1.session_id)
        await voting_service.cast_vote(
            session1.session_id, "player_001", "Alice", "player_002", "Bob"
        )

        session2 = await voting_service.create_vote_session(
            game_session_id="game_015",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002"]
        )
        await voting_service.start_voting(session2.session_id)
        await voting_service.cast_vote(
            session2.session_id, "player_001", "Alice", "player_003", "Charlie"
        )

        history = await voting_service.get_player_vote_history("player_001")

        assert len(history) == 2
        assert history[0]["vote_type"] == "detective_mid"
        assert history[0]["voted_for"] == "Bob"
        assert history[1]["vote_type"] == "final"
        assert history[1]["voted_for"] == "Charlie"

    @pytest.mark.asyncio
    async def test_get_empty_vote_history(self, voting_service):
        """Test history for player with no votes."""
        history = await voting_service.get_player_vote_history("player_no_votes")
        assert history == []


class TestHasVoted:
    """Test has voted check."""

    @pytest.mark.asyncio
    async def test_has_voted_true(self, voting_service):
        """Test checking voted status - voted."""
        session = await voting_service.create_vote_session(
            game_session_id="game_016",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002"]
        )
        await voting_service.start_voting(session.session_id)
        await voting_service.cast_vote(
            session.session_id, "player_001", "Alice", "player_002", "Bob"
        )

        has_voted = await voting_service.has_voted(session.session_id, "player_001")
        assert has_voted is True

    @pytest.mark.asyncio
    async def test_has_voted_false(self, voting_service):
        """Test checking voted status - not voted."""
        session = await voting_service.create_vote_session(
            game_session_id="game_017",
            vote_type=VoteType.FINAL,
            eligible_voters=["player_001", "player_002"]
        )
        await voting_service.start_voting(session.session_id)

        has_voted = await voting_service.has_voted(session.session_id, "player_001")
        assert has_voted is False

    @pytest.mark.asyncio
    async def test_has_voted_session_not_found(self, voting_service):
        """Test checking voted status for non-existent session."""
        has_voted = await voting_service.has_voted("invalid_session", "player_001")
        assert has_voted is False
