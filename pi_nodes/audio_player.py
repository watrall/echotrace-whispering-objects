"""Audio playback helpers for EchoTrace node devices (scaffold)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - executed when pygame is available
    from pygame import mixer
except ImportError:  # pragma: no cover - executed in test/mock environments
    mixer = None  # type: ignore[assignment]


LOGGER = logging.getLogger(__name__)


class AudioPlayer:
    """Provide a minimal abstraction over pygame.mixer for scaffold purposes."""

    def __init__(self) -> None:
        self._loaded_path: Optional[Path] = None
        self._active: bool = False
        self._mixer_available = mixer is not None
        if self._mixer_available and not mixer.get_init():  # type: ignore[union-attr]
            mixer.init()  # type: ignore[union-attr]
            LOGGER.debug("pygame.mixer initialised in scaffold mode.")

    def load(self, path: Path) -> None:
        """Store the path to the audio file to be played later."""
        self._loaded_path = path
        LOGGER.debug("Audio asset queued: %s", path)

    def set_volume(self, value_0_to_1: float) -> None:
        """Adjust output volume if the mixer is present."""
        if not self._mixer_available or mixer is None:
            LOGGER.debug("Volume request ignored; mixer unavailable.")
            return
        mixer.music.set_volume(max(0.0, min(1.0, value_0_to_1)))  # type: ignore[union-attr]

    def play(self, loop: bool = False, pace: float = 1.0) -> None:  # noqa: ARG002
        """Start playback for the loaded clip if supported."""
        if self._loaded_path is None:
            LOGGER.warning("No audio loaded; play() ignored.")
            return
        if not self._mixer_available or mixer is None:
            LOGGER.info("Play request for %s ignored; mixer unavailable.", self._loaded_path)
            return
        mixer.music.load(str(self._loaded_path))  # type: ignore[union-attr]
        mixer.music.play(-1 if loop else 0)  # type: ignore[union-attr]
        self._active = True

    def stop(self) -> None:
        """Stop playback when supported."""
        if not self._mixer_available or mixer is None:
            LOGGER.debug("Stop request ignored; mixer unavailable.")
            return
        mixer.music.stop()  # type: ignore[union-attr]
        self._active = False


__all__ = ["AudioPlayer"]
