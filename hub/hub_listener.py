"""Placeholder MQTT listener for the EchoTrace hub."""

from __future__ import annotations

import logging
import time
from typing import NoReturn


LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure basic logging for the hub listener."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run_forever() -> NoReturn:
    """Run a placeholder loop to simulate listener behaviour."""
    configure_logging()
    LOGGER.info("Hub listener started (scaffold mode).")
    try:
        while True:
            LOGGER.debug("Hub listener heartbeat.")
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        LOGGER.info("Hub listener stopped.")
        raise


if __name__ == "__main__":
    run_forever()
