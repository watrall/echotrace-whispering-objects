"""Utilities for loading, persisting, and deriving accessibility profiles."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

ACCESSIBILITY_PATH = Path(__file__).resolve().parent / "accessibility_profiles.yaml"


def load_profiles(path: Path | None = None) -> dict[str, Any]:
    """Load accessibility profiles from disk."""
    target = path or ACCESSIBILITY_PATH
    if not target.exists():
        return {"global": {}, "presets": {}, "per_node_overrides": {}}
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Accessibility profiles file must contain a mapping.")
    data.setdefault("global", {})
    data.setdefault("presets", {})
    data.setdefault("per_node_overrides", {})
    return data


def save_profiles(profiles: dict[str, Any], path: Path | None = None) -> None:
    """Persist accessibility profiles to disk."""
    target = path or ACCESSIBILITY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(profiles, handle, sort_keys=True)


def apply_preset(profiles: dict[str, Any], preset_name: str) -> dict[str, Any]:
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


def set_per_node_override(
    profiles: dict[str, Any],
    node_id: str,
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Persist per-node overrides, removing entries when overrides are empty."""
    per_node = profiles.setdefault("per_node_overrides", {})
    if not isinstance(per_node, dict):
        raise ValueError("per_node_overrides must be a mapping.")
    normalised = {key: value for key, value in overrides.items() if value not in (None, "")}
    if normalised:
        per_node[node_id] = normalised
    else:
        per_node.pop(node_id, None)
    return profiles


def derive_runtime_payloads(
    profiles: dict[str, Any],
    nodes: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return node-specific configuration payloads derived from accessibility settings."""
    global_settings = _ensure_mapping(profiles.get("global"))
    overrides = _ensure_mapping(profiles.get("per_node_overrides"))

    payloads: dict[str, dict[str, Any]] = {}
    for node_id in nodes.keys():
        node_override = _ensure_mapping(overrides.get(node_id))
        payloads[node_id] = _build_node_payload(global_settings, node_override)
    return payloads


def _build_node_payload(
    global_settings: dict[str, Any],
    node_override: dict[str, Any],
) -> dict[str, Any]:
    captions = bool(node_override.get("captions", global_settings.get("captions", False)))
    visual_pulse = bool(node_override.get("visual_pulse", False))
    proximity_glow = bool(node_override.get("proximity_glow", True))
    default_buffer = _clamp_int(global_settings.get("mobility_buffer_ms", 800), 0, 60000)
    mobility_buffer_ms = _clamp_int(
        node_override.get("mobility_buffer_ms", default_buffer),
        0,
        60000,
    )
    repeat = _clamp_int(node_override.get("repeat", 0), 0, 2)
    base_pace = 0.9 if global_settings.get("sensory_friendly") else 1.0
    pace = _clamp_float(node_override.get("pace", base_pace), 0.85, 1.15)
    safety_limiter = bool(
        node_override.get("safety_limiter", global_settings.get("safety_limiter", True))
    )

    volume = node_override.get("volume")
    if volume is None:
        volume = 0.7
        if global_settings.get("sensory_friendly"):
            volume = min(volume, 0.55)
        if global_settings.get("quiet_hours"):
            volume = min(volume, 0.45)
    volume = _clamp_float(volume, 0.0, 1.0)

    accessibility_payload = {
        "captions": captions,
        "visual_pulse": visual_pulse,
        "proximity_glow": proximity_glow,
        "mobility_buffer_ms": max(0, mobility_buffer_ms),
        "repeat": repeat,
        "pace": pace,
        "safety_limiter": safety_limiter,
    }

    return {
        "audio": {"volume": volume},
        "accessibility": accessibility_payload,
    }


def _ensure_mapping(candidate: Any) -> dict[str, Any]:
    if isinstance(candidate, Mapping):
        return dict(candidate)
    return {}


def _clamp_int(value: Any, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum
    return max(minimum, min(maximum, number))


def _clamp_float(value: Any, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = minimum
    return max(minimum, min(maximum, number))


__all__ = [
    "ACCESSIBILITY_PATH",
    "apply_preset",
    "derive_runtime_payloads",
    "load_profiles",
    "save_profiles",
    "set_per_node_override",
]
