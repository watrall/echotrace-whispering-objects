"""Narrative state tracking for the EchoTrace hub."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class NarrativeState:
    """Track triggered fragments and whether the mystery narrative is unlocked."""

    required_fragments: int
    triggered_whispers: Set[str] = field(default_factory=set)
    unlocked: bool = False

    def register_trigger(self, node_id: str) -> bool:
        """
        Record that a whisper node has triggered.

        Returns True when the trigger is newly recorded, False for duplicates.
        """
        if node_id in self.triggered_whispers:
            return False
        self.triggered_whispers.add(node_id)
        if not self.unlocked and len(self.triggered_whispers) >= self.required_fragments:
            self.unlocked = True
        return True

    def reset(self) -> None:
        """Clear tracked triggers and reset unlock status."""
        self.triggered_whispers.clear()
        self.unlocked = False

    def snapshot(self) -> Dict[str, object]:
        """Return a serialisable view of the current narrative state."""
        return {
            "unlocked": self.unlocked,
            "triggered": self.triggered_list(),
        }

    def triggered_list(self) -> List[str]:
        """Expose the triggered whisper identifiers sorted for readability."""
        return sorted(self.triggered_whispers)


__all__ = ["NarrativeState"]
