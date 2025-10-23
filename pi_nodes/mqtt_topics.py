"""Node-side MQTT topic helpers (duplicated scaffold)."""

from __future__ import annotations

from typing import Final


PREFIX: Final[str] = "ECHOTRACE"


def health_topic(node_id: str) -> str:
    """Return the health topic for the provided node identifier."""
    return f"{PREFIX}/health/{node_id}"


def trigger_topic(node_id: str) -> str:
    """Return the trigger topic for the provided node identifier."""
    return f"{PREFIX}/trigger/{node_id}"


def hub_state_topic() -> str:
    """Return the topic where the hub publishes state updates."""
    return f"{PREFIX}/state/hub"


def node_config_topic(node_id: str) -> str:
    """Return the configuration topic for this node."""
    return f"{PREFIX}/config/{node_id}"


def node_ack_topic(node_id: str) -> str:
    """Return the acknowledgement topic for this node."""
    return f"{PREFIX}/ack/{node_id}"

