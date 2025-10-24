"""Haptic feedback helper for EchoTrace nodes (scaffold)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

try:  # pragma: no cover - executed when gpiozero is installed
    from gpiozero import DigitalOutputDevice as _HardwareOutputDevice
except ImportError:  # pragma: no cover - executed in test/mock environments
    _HardwareOutputDevice = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - typing aid only
    from gpiozero import DigitalOutputDevice as _OutputDeviceBase  # type: ignore
else:

    class _OutputDeviceBase:  # type: ignore[too-many-instance-attributes]
        """Fallback implementation used when gpiozero is not available."""

        def __init__(self, pin: int, active_high: bool = True) -> None:  # noqa: D401
            self.pin = pin
            self.state = False
            self.active_high = active_high

        def blink(self, on_time: float, off_time: float, n: int | None = None) -> None:
            self.state = True

        def on(self) -> None:
            self.state = True

        def off(self) -> None:
            self.state = False

        def close(self) -> None:
            self.off()


LOGGER = logging.getLogger(__name__)


class Haptics:
    """Provide a minimal wrapper for toggling a vibration motor."""

    def __init__(self, pin: int, active_high: bool = True) -> None:
        if _HardwareOutputDevice is not None:
            self._device: _OutputDeviceBase = _HardwareOutputDevice(pin, active_high=active_high)
        else:
            self._device = _OutputDeviceBase(pin, active_high=active_high)
        LOGGER.debug("Haptics initialised on pin %s", pin)

    def pulse(self, ms: int) -> None:
        """Emit a simple pulse of the requested duration."""
        seconds = max(0, ms) / 1000
        self._device.blink(on_time=seconds, off_time=0.01, n=1)
        LOGGER.debug("Haptic pulse triggered for %sms", ms)

    def off(self) -> None:
        """Ensure the haptic driver is inactive."""
        self._device.off()

    def close(self) -> None:
        """Release the underlying GPIO resource."""
        self._device.close()


__all__ = ["Haptics"]
