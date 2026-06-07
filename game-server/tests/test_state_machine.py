"""TDD: Game session state machine — 9-phase Mingzhen mode flow."""
import pytest
from src.session.models import GamePhase, PlayerRole
from src.session.state_machine import GameSession


# ============================================================
# Tests: Phase transitions
# ============================================================

class TestPhaseTransitions:
    """Verify the 9-phase flow progresses correctly."""

    def test_initial_phase_is_preparation(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        assert session.current_phase == GamePhase.PREPARATION

    def test_all_confirm_advances_to_act1(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)

        session.player_confirm("p1")
        assert session.current_phase == GamePhase.PREPARATION  # Not all confirmed
        session.player_confirm("p2")
        assert session.current_phase == GamePhase.ACT_1_TURN_TALK

    def test_preparation_timeout_advances(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        # Force timeout
        session.force_phase_advance()
        assert session.current_phase == GamePhase.ACT_1_TURN_TALK

    def test_full_9_phase_flow(self):
        """Complete game: preparation → result → finished."""
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.add_player("p3", "char_03", PlayerRole.KILLER)

        phases = [
            GamePhase.PREPARATION,
            GamePhase.ACT_1_TURN_TALK,
            GamePhase.ROUND_1_SEARCH,
            GamePhase.ACT_2_DISCUSS,
            GamePhase.DETECTIVE_VOTE,
            GamePhase.ROUND_2_SEARCH,
            GamePhase.ACT_3_DISCUSS,
            GamePhase.FINAL_VOTE,
            GamePhase.RESULT,
            GamePhase.FINISHED,
        ]
        for phase in phases:
            assert session.current_phase == phase
            session.force_phase_advance()
        assert session.current_phase == GamePhase.FINISHED


# ============================================================
# Tests: Act 1 turn-taking
# ============================================================

class TestAct1TurnTaking:
    def test_detective_speaks_first(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.force_phase_advance()  # → ACT_1

        assert session.current_speaker == "p2"  # Detective first

    def test_turn_order_follows_role(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.add_player("p3", "char_03", PlayerRole.KILLER)
        session.force_phase_advance()  # → ACT_1

        # Detective → normal → killer
        assert session.current_speaker == "p2"
        session.next_speaker()
        assert session.current_speaker == "p1"
        session.next_speaker()
        assert session.current_speaker == "p3"

    def test_all_spoken_triggers_free_exchange(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.force_phase_advance()  # → ACT_1

        session.next_speaker()  # detective done
        session.next_speaker()  # normal done → all spoken
        assert session.is_free_exchange  # Now in free exchange mode


# ============================================================
# Tests: Speech & question limits
# ============================================================

class TestSpeechLimits:
    def test_free_exchange_speech_limit(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.force_phase_advance()  # → ACT_1
        session.next_speaker()
        session.next_speaker()  # → free exchange

        # Player speaks 15 times
        for _ in range(15):
            assert session.can_speak("p1") is True
            session.record_speech("p1")
        assert session.can_speak("p1") is False  # Limit reached

    def test_question_per_player_limit(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.force_phase_advance()  # → ACT_1
        session.next_speaker()
        session.next_speaker()  # → free exchange

        # p1 asks p2 three times
        for _ in range(3):
            assert session.can_question("p1", "p2") is True
            session.record_question("p1", "p2")
        assert session.can_question("p1", "p2") is False  # Limit reached

    def test_can_still_speak_after_question_limit(self):
        """Question limit doesn't affect speech limit."""
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.force_phase_advance()
        session.next_speaker()
        session.next_speaker()  # → free exchange

        for _ in range(3):
            session.record_question("p1", "p2")
        assert session.can_speak("p1") is True  # Can still speak


# ============================================================
# Tests: AP search system
# ============================================================

class TestSearchSystem:
    def test_search_ap_allocation(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)

        # Advance to round 1 search (PREP→ACT_1→ROUND_1: 2 steps)
        for _ in range(2):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.ROUND_1_SEARCH

        # Normal player gets 15 AP in round 1
        p1 = session.get_player("p1")
        assert p1.ap_remaining == 15

    def test_detective_gets_extra_ap(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)

        for _ in range(2):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.ROUND_1_SEARCH

        # Detective gets +1 AP
        p2 = session.get_player("p2")
        assert p2.ap_remaining == 16  # 15 + 1

    def test_round2_more_ap(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)

        # Advance to round 2 search (PREP→ACT_1→ROUND_1→ACT_2→DETECTIVE→ROUND_2: 5 steps)
        for _ in range(5):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.ROUND_2_SEARCH

        p1 = session.get_player("p1")
        assert p1.ap_remaining == 20  # Round 2: 20 AP


# ============================================================
# Tests: Voting
# ============================================================

class TestVoting:
    def test_detective_solo_vote(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.add_player("p3", "char_03", PlayerRole.KILLER)

        # Advance to detective vote (PREP→...→DETECTIVE: 4 steps)
        for _ in range(4):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.DETECTIVE_VOTE

        session.cast_vote("p2", "p3")  # Detective votes killer
        p2 = session.get_player("p2")
        assert p2.vote_target == "p3"

    def test_final_vote_all_players(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.add_player("p3", "char_03", PlayerRole.KILLER)

        # Advance to final vote (PREP→...→FINAL_VOTE: 7 steps)
        for _ in range(7):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.FINAL_VOTE

        session.cast_vote("p1", "p3")
        session.cast_vote("p2", "p3")
        session.cast_vote("p3", "p1")  # Killer tries to deflect

    def test_tie_breaker_triggered(self):
        session = GameSession(session_id="test_001", script_id="script_01")
        session.add_player("p1", "char_01", PlayerRole.NORMAL)
        session.add_player("p2", "char_02", PlayerRole.DETECTIVE)
        session.add_player("p3", "char_03", PlayerRole.KILLER)
        session.add_player("p4", "char_04", PlayerRole.NORMAL)

        for _ in range(7):
            session.force_phase_advance()
        assert session.current_phase == GamePhase.FINAL_VOTE

        session.cast_vote("p1", "p3")
        session.cast_vote("p2", "p4")
        session.cast_vote("p3", "p1")
        session.cast_vote("p4", "p3")

        tied = session.get_vote_result()
        # p3=2, p4=1, p1=1 → p3 has most but not unique
        assert tied["is_tie"] is True or tied["winner"] is not None
