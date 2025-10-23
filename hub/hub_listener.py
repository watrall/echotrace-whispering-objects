"""Placeholder MQTT listener for the EchoTrace hub."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, NoReturn

from .logging_utils import CsvEventLogger


@dataclass
class HubRuntimeState:
    """In-memory snapshot of hub observability data."""

    last_seen: Dict[str, datetime] = field(default_factory=dict)

    def update_health(self, node_id: str, timestamp: datetime) -> None:
        """Record the last time a heartbeat was observed for a node."""
        self.last_seen[node_id] = timestamp

    def snapshot(self) -> Dict[str, float]:
        """Return seconds elapsed since the last heartbeat per node."""
        now = datetime.now(tz=timezone.utc)
        return {
            node_id: (now - seen).total_seconds()
            for node_id, seen in self.last_seen.items()
        }


LOGGER = logging.getLogger(__name__)
STATE = HubRuntimeState()
EVENT_LOGGER = CsvEventLogger(Path("hub/logs"))


def configure_logging() -> None:
    """Configure basic logging for the hub listener."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run_forever() -> NoReturn:
    """Run a placeholder loop to simulate listener behaviour."""
    configure_logging()
    LOGGER.info("Hub listener started (scaffold mode).")
    try:
        while True:
            timestamp = datetime.now(tz=timezone.utc)
            STATE.update_health("hub-scaffold", timestamp)
            EVENT_LOGGER.record_event("listener_heartbeat", "hub", "Scaffold loop tick")
            LOGGER.debug("Hub listener heartbeat snapshot: %s", STATE.snapshot())
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        LOGGER.info("Hub listener stopped.")
        raise


if __name__ == "__main__":
    run_forever()
