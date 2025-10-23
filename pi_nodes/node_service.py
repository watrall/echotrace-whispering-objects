"""Scaffold node service loop for EchoTrace devices."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

import yaml

from .proximity_sensor import ProximitySensor
from .logging_utils import configure_node_logging

LOGGER = logging.getLogger(__name__)


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "node_config.yaml"


class NodeService:
    """Minimal node service that emits heartbeat logs."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.node_id: str = "node-unknown"
        self.node_role: str = "whisper"
        self.sensor = ProximitySensor()
        self._load_config()

    def _load_config(self) -> None:
        """Load YAML configuration for the node service."""
        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                self.config = yaml.safe_load(handle) or {}
        except FileNotFoundError:
            LOGGER.warning("Node configuration %s not found; using defaults.", self.config_path)
            self.config = {"node_id": "node-unknown"}
        except yaml.YAMLError as exc:
            raise RuntimeError(f"Invalid node configuration YAML: {exc}") from exc

        self.node_id = str(self.config.get("node_id", "node-unknown"))
        self.node_role = str(self.config.get("role", "whisper"))

    def run_once(self) -> Dict[str, Any]:
        """Execute a single iteration of the service logic."""
        distance = self.sensor.read_distance_mm()
        payload = {
            "node_id": self.node_id,
            "role": self.node_role,
            "distance_mm": distance,
            "timestamp": time.time(),
        }
        LOGGER.debug("Heartbeat payload: %s", json.dumps(payload))
        return payload

    def run_forever(self, interval_seconds: float = 15.0) -> None:
        """Run the service loop indefinitely with a simple sleep."""
        LOGGER.info("Node service starting (scaffold mode).")
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:  # pragma: no cover - manual stop
            LOGGER.info("Node service terminated by user.")
            raise


def main() -> None:
    """Entry point used by system service scaffolds."""
    configure_node_logging()
    NodeService().run_forever()


if __name__ == "__main__":
    main()
