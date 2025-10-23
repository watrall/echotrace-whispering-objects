"""Tests for the NarrativeState helper."""

from __future__ import annotations

from hub.narrative_state import NarrativeState


def test_narrative_unlocks_after_required_triggers() -> None:
    """Narrative should unlock after required unique triggers."""
    state = NarrativeState(required_fragments=2)
    assert state.register_trigger("node1") is True
    assert state.unlocked is False
    assert state.register_trigger("node1") is False
    assert state.unlocked is False

    state.register_trigger("node2")
    assert state.unlocked is True
    snapshot = state.snapshot()
    assert snapshot["unlocked"] is True
    assert snapshot["triggered"] == ["node1", "node2"]

    state.reset()
    assert state.unlocked is False
    assert state.snapshot()["triggered"] == []
