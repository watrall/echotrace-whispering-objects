"""Simple content pack manager stub for the EchoTrace hub."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ContentPack:
    """Lightweight record describing a content pack."""

    name: str
    path: Path


class ContentManager:
    """Provide minimal helpers for locating content packs."""

    def __init__(self, packs_root: Path | None = None) -> None:
        self._packs_root = packs_root or Path("content-packs")

    def list_packs(self) -> List[str]:
        """Return discovered content pack directory names."""
        if not self._packs_root.exists():
            return []
        return [item.name for item in self._packs_root.iterdir() if item.is_dir()]

    def load_pack(self, name: str) -> ContentPack:
        """Return a lightweight ContentPack pointing at the given name."""
        pack_path = self._packs_root / name
        if not pack_path.exists():
            raise FileNotFoundError(f"Content pack '{name}' not found at {pack_path}")
        return ContentPack(name=name, path=pack_path)

