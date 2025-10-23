"""Scaffold node service loop for EchoTrace devices."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:  # pragma: no cover - executed when PyYAML is missing
    yaml = None  # type: ignore[assignment]

from .proximity_sensor import ProximitySensor

LOGGER = logging.getLogger(__name__)


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "node_config.yaml"


def _parse_basic_yaml(text: str) -> Dict[str, Any]:
    """Parse a minimal subset of YAML syntax when PyYAML is unavailable."""
    result: Dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        result[key.strip()] = value.strip()
    return result


class NodeService:
    """Minimal node service that emits heartbeat logs."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.sensor = ProximitySensor()
        self._load_config()

    def _load_config(self) -> None:
        """Load YAML configuration for the node service."""
        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                if yaml is None:
                    LOGGER.warning("PyYAML unavailable; using fallback parser.")
                    self.config = _parse_basic_yaml(handle.read())
                else:
                    self.config = yaml.safe_load(handle) or {}
        except FileNotFoundError:
            LOGGER.warning("Node configuration %s not found; using defaults.", self.config_path)
            self.config = {"node_id": "node-unknown"}

    def run_once(self) -> Dict[str, Any]:
        """Execute a single iteration of the service logic."""
        distance = self.sensor.read_distance_mm()
        payload = {
            "node_id": self.config.get("node_id", "node-unknown"),
            "distance_mm": distance,
            "timestamp": time.time(),
        }
        LOGGER.debug("Heartbeat payload: %s", json.dumps(payload))
        return payload

    def run_forever(self, interval_seconds: float = 5.0) -> None:
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    NodeService().run_forever()


if __name__ == "__main__":
    main()
