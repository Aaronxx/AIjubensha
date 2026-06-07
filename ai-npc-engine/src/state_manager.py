"""Game session and NPC state management."""
from __future__ import annotations

import re

from .models import (
    ArcState,
    ArcTransition,
    InfoLevel,
    KnowledgeEntry,
    NPCDefinition,
    NPCState,
)
from .prompt import EMOTION_CALM


class StateManager:
    """Manages NPC state updates and arc transitions during gameplay."""

    def update_after_reply(
        self,
        npc_def: NPCDefinition,
        npc_state: NPCState,
        player_id: str,
        parsed_output: dict,
    ):
        """Update NPC state based on the structured output from LLM."""
        # Update emotional tag
        new_tag = parsed_output.get("emotional_tag")
        if new_tag:
            npc_state.emotional_tag = new_tag

        # Record revealed info
        for info in parsed_output.get("info_revealed", []):
            fact_id = self._find_fact_id(npc_def, info.get("content", ""))
            if fact_id:
                npc_state.record_release(fact_id, player_id)

        # Check arc state transition
        shift = parsed_output.get("attitude_shift")
        if shift:
            self._apply_attitude_shift(npc_state, shift)

        # Check if any arc transition conditions are met
        self._check_arc_transitions(npc_def, npc_state)

    def _find_fact_id(self, npc_def: NPCDefinition, content_hint: str) -> str | None:
        """Match revealed info content to a known fact_id using keyword overlap."""
        if not content_hint or len(content_hint) < 3:
            return None

        best_match = None
        best_score = 0

        for entry in npc_def.knowledge:
            if entry.released:
                continue
            score = self._similarity_score(content_hint, entry.content)
            if score > best_score:
                best_score = score
                best_match = entry.fact_id

        # Require minimum similarity threshold
        return best_match if best_score >= 0.2 else None

    def _similarity_score(self, a: str, b: str) -> float:
        """Calculate keyword overlap score between two strings.

        1. Exact substring match → 1.0
        2. Extract 2-char bigrams and calculate Jaccard-like overlap
        3. Weight longer common substrings higher
        """
        if a in b or b in a:
            return 1.0

        # Tokenize into 2-4 char grams for Chinese text
        def grams(s: str, n: int) -> set:
            return {s[i:i+n] for i in range(len(s) - n + 1)}

        # Multi-scale overlap: bigrams + trigrams
        score = 0.0
        for n in [3, 2]:
            g_a = grams(a, n)
            g_b = grams(b, n)
            if g_a and g_b:
                overlap = len(g_a & g_b)
                total = min(len(g_a), len(g_b))
                if total > 0:
                    score = max(score, overlap / total)
        return score

    def _apply_attitude_shift(self, npc_state: NPCState, shift_str: str):
        """Parse attitude shift like '+0.2，玩家展现了对我的信任'."""
        match = re.search(r"([+-]?\d*\.?\d+)", shift_str)
        if match:
            delta = float(match.group(1))
            npc_state.attitude_to_player = max(-1.0, min(1.0, npc_state.attitude_to_player + delta))

    def _check_arc_transitions(self, npc_def: NPCDefinition, npc_state: NPCState):
        """Check if current state should transition. Recursively chains forward.

        Forward = toward more open/defensive/breakdown states.
        Recovery (defensive→polite etc.) only triggers on separate update calls,
        not within the same chain — simulating that rebuilding trust takes time.
        """
        visited = set()
        while True:
            current = npc_state.current_arc_state
            if current in visited:
                break
            visited.add(current)
            found = False
            for t in npc_def.arc_transitions:
                if t.from_state == current:
                    # Skip recovery transitions in chains (backward movement)
                    # Recovery requires a fresh update call
                    if t.to_state in visited:
                        continue
                    if self._evaluate_trigger(t, npc_state):
                        npc_state.current_arc_state = t.to_state
                        found = True
                        break
            if not found:
                break

    def _evaluate_trigger(self, transition: ArcTransition, npc_state: NPCState) -> bool:
        """Evaluate a transition trigger condition using regex parsing.

        Supported formats:
          attitude>=X   attitude<=X   attitude>X   attitude<X
          emotion==X    emotion!=X    emotion_contains=X
          combined: "attitude>=0.3 AND emotion_contains=紧张"
        """
        condition = transition.trigger_condition

        # Check for AND combos
        if " AND " in condition:
            parts = condition.split(" AND ")
            return all(self._evaluate_single(p.strip(), npc_state) for p in parts)

        return self._evaluate_single(condition, npc_state)

    def _evaluate_single(self, condition: str, npc_state: NPCState) -> bool:
        # emotion operators
        m = re.match(r'emotion==(.+)', condition)
        if m:
            return npc_state.emotional_tag == m.group(1).strip()

        m = re.match(r'emotion!= (.+)', condition)
        if m:
            return npc_state.emotional_tag != m.group(1).strip()

        m = re.match(r'emotion_contains=(.+)', condition)
        if m:
            return m.group(1).strip() in npc_state.emotional_tag

        # attitude operators (regex avoids ambiguity between >= and >)
        m = re.match(r'attitude([><]=?)\s*(-?[\d.]+)', condition)
        if m:
            op, val = m.group(1), float(m.group(2))
            if op == ">=":
                return npc_state.attitude_to_player >= val
            elif op == "<=":
                return npc_state.attitude_to_player <= val
            elif op == ">":
                return npc_state.attitude_to_player > val
            elif op == "<":
                return npc_state.attitude_to_player < val

        return False

    def init_npc_state(self, npc_def: NPCDefinition) -> NPCState:
        """Create initial NPC state from definition."""
        knowledge_map = {}
        for k in npc_def.knowledge:
            entry = KnowledgeEntry(
                fact_id=k.fact_id,
                level=k.level,
                content=k.content,
                release_condition=k.release_condition,
                time_label=k.time_label,
                location_label=k.location_label,
                released=k.released,
                released_to=list(k.released_to),
            )
            knowledge_map[k.fact_id] = entry

        initial_arc = npc_def.initial_arc_state or (
            npc_def.arc_states[0].name if npc_def.arc_states else "default"
        )

        return NPCState(
            npc_id=npc_def.npc_id,
            current_arc_state=initial_arc,
            emotional_tag=EMOTION_CALM,
            attitude_to_player=0.0,
            knowledge_map=knowledge_map,
        )
