"""Proximity sensor abstraction for EchoTrace nodes (scaffold)."""

from __future__ import annotations

import logging
from typing import Optional

LOGGER = logging.getLogger(__name__)


class ProximitySensor:
    """Return a fixed distance when hardware is unavailable."""

    def __init__(self, i2c_bus: Optional[int] = None, address: Optional[int] = None) -> None:  # noqa: D401
        """Initialise the sensor placeholder; arguments kept for future compatibility."""
        self._i2c_bus = i2c_bus
        self._address = address
        LOGGER.debug(
            "ProximitySensor placeholder initialised (bus=%s, address=%s)",
            i2c_bus,
            address,
        )

    def read_distance_mm(self) -> Optional[int]:
        """Return a fixed distance measurement representing 'no visitor'."""
        return 900


class MockProximitySensor(ProximitySensor):
    """Simple mockable proximity sensor used in tests."""

    def __init__(self, distances: Optional[list[int]] = None) -> None:
        super().__init__()
        self._distances = distances or [900]
        self._index = 0

    def read_distance_mm(self) -> Optional[int]:
        if not self._distances:
            return None
        result = self._distances[min(self._index, len(self._distances) - 1)]
        self._index += 1
        return result


__all__ = ["ProximitySensor", "MockProximitySensor"]
