"""Utilities for loading and persisting accessibility profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

ACCESSIBILITY_PATH = Path(__file__).resolve().parent / "accessibility_profiles.yaml"


def load_profiles(path: Path | None = None) -> Dict[str, Any]:
    """Load accessibility profiles from disk."""
    target = path or ACCESSIBILITY_PATH
    if not target.exists():
        return {"global": {}, "presets": {}, "per_node_overrides": {}}
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Accessibility profiles file must contain a mapping.")
    return data


def save_profiles(profiles: Dict[str, Any], path: Path | None = None) -> None:
    """Persist accessibility profiles to disk."""
    target = path or ACCESSIBILITY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(profiles, handle, sort_keys=True)


def apply_preset(profiles: Dict[str, Any], preset_name: str) -> Dict[str, Any]:
    """Apply a preset to the global accessibility configuration."""
    presets = profiles.get("presets", {})
    if preset_name not in presets:
        raise KeyError(f"Preset '{preset_name}' not found.")
    global_settings = profiles.setdefault("global", {})
    preset_values = presets[preset_name] or {}
    if not isinstance(global_settings, dict):
        raise ValueError("Global accessibility settings must be a mapping.")
    if not isinstance(preset_values, dict):
        raise ValueError("Preset values must be a mapping.")
    global_settings.update(preset_values)
    return profiles


__all__ = ["ACCESSIBILITY_PATH", "apply_preset", "load_profiles", "save_profiles"]
