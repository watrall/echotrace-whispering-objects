"""Configuration loading utilities for the EchoTrace hub."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


class ConfigError(RuntimeError):
    """Raised when a configuration file cannot be parsed or validated."""


@dataclass(frozen=True)
class AnalyticsConfig:
    """Configuration values governing analytics logging."""

    enable_csv: bool = True
    rotation_daily: bool = True


@dataclass(frozen=True)
class NarrativeConfig:
    """Parameters that control the narrative unlock behaviour."""

    required_fragments_to_unlock: int = 4


@dataclass(frozen=True)
class SecurityConfig:
    """Settings that secure access to the administrative dashboard."""

    require_basic_auth: bool = True
    admin_user_env: str = "ECHOTRACE_ADMIN_USER"
    admin_pass_env: str = "ECHOTRACE_ADMIN_PASS"


@dataclass(frozen=True)
class HubConfig:
    """Top-level hub configuration."""

    broker_host: str
    broker_port: int
    dashboard_host: str
    dashboard_port: int
    default_language: str
    logs_dir: Path
    analytics: AnalyticsConfig
    narrative: NarrativeConfig
    security: SecurityConfig


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config(path: Path | None = None) -> HubConfig:
    """Load and validate the hub configuration file."""
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            parsed = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:  # type: ignore[attr-defined]
        raise ConfigError(f"Failed to parse configuration: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read configuration: {exc}") from exc

    if not isinstance(parsed, Mapping):
        raise ConfigError("Configuration root must be a mapping/object.")

    broker_host = _require_str(parsed, "broker_host", default="localhost")
    broker_port = _require_int(parsed, "broker_port", default=1883, minimum=1)
    dashboard_host = _require_str(parsed, "dashboard_host", default="0.0.0.0")
    dashboard_port = _require_int(parsed, "dashboard_port", default=8080, minimum=1)
    default_language = _require_str(parsed, "default_language", default="en")
    logs_dir_raw = _require_str(parsed, "logs_dir", default="hub/logs")
    logs_dir = Path(logs_dir_raw)
    logs_dir.mkdir(parents=True, exist_ok=True)

    analytics = _load_analytics(parsed.get("analytics"))
    narrative = _load_narrative(parsed.get("narrative"))
    security = _load_security(parsed.get("security"))

    return HubConfig(
        broker_host=broker_host,
        broker_port=broker_port,
        dashboard_host=dashboard_host,
        dashboard_port=dashboard_port,
        default_language=default_language,
        logs_dir=logs_dir,
        analytics=analytics,
        narrative=narrative,
        security=security,
    )


def _load_analytics(section: Any) -> AnalyticsConfig:
    data = _coerce_mapping(section, "analytics")
    enable_csv = _require_bool(data, "enable_csv", default=True)
    rotation_daily = _require_bool(data, "rotation_daily", default=True)
    return AnalyticsConfig(enable_csv=enable_csv, rotation_daily=rotation_daily)


def _load_narrative(section: Any) -> NarrativeConfig:
    data = _coerce_mapping(section, "narrative")
    required = _require_int(data, "required_fragments_to_unlock", default=4, minimum=1)
    return NarrativeConfig(required_fragments_to_unlock=required)


def _load_security(section: Any) -> SecurityConfig:
    data = _coerce_mapping(section, "security")
    require_basic_auth = _require_bool(data, "require_basic_auth", default=True)
    admin_user_env = _require_str(data, "admin_user_env", default="ECHOTRACE_ADMIN_USER")
    admin_pass_env = _require_str(data, "admin_pass_env", default="ECHOTRACE_ADMIN_PASS")
    return SecurityConfig(
        require_basic_auth=require_basic_auth,
        admin_user_env=admin_user_env,
        admin_pass_env=admin_pass_env,
    )


def _coerce_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ConfigError(f"Section '{label}' must be a mapping/object.")
    return value


def _require_str(source: Mapping[str, Any], key: str, default: str | None = None) -> str:
    value = source.get(key, default)
    if value is None:
        raise ConfigError(f"Missing configuration key: {key}")
    if not isinstance(value, str) or not value:
        raise ConfigError(f"Configuration key '{key}' must be a non-empty string.")
    return value


def _require_int(
    source: Mapping[str, Any],
    key: str,
    default: int | None = None,
    *,
    minimum: int | None = None,
) -> int:
    value = source.get(key, default)
    if value is None:
        raise ConfigError(f"Missing configuration key: {key}")
    if not isinstance(value, int):
        raise ConfigError(f"Configuration key '{key}' must be an integer.")
    if minimum is not None and value < minimum:
        raise ConfigError(f"Configuration key '{key}' must be >= {minimum}.")
    return value


def _require_bool(
    source: Mapping[str, Any],
    key: str,
    default: bool | None = None,
) -> bool:
    value = source.get(key, default)
    if value is None:
        raise ConfigError(f"Missing configuration key: {key}")
    if not isinstance(value, bool):
        raise ConfigError(f"Configuration key '{key}' must be a boolean.")
    return value


__all__ = [
    "AnalyticsConfig",
    "ConfigError",
    "HubConfig",
    "NarrativeConfig",
    "SecurityConfig",
    "load_config",
]
