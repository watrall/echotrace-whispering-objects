"""MQTT listener coordinating node messages for the EchoTrace hub."""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

try:  # pragma: no cover - executed when paho-mqtt is installed
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - executed in environments without paho-mqtt
    mqtt = None  # type: ignore[assignment]

from .config_loader import HubConfig, load_config
from .logging_utils import CsvEventLogger
from .mqtt_topics import (
    ack_wildcard,
    health_topic,
    health_wildcard,
    hub_state_topic,
    node_ack_topic,
    node_config_topic,
    trigger_wildcard,
)
from .narrative_state import NarrativeState

LOGGER = logging.getLogger(__name__)

_HEALTH_PREFIX = health_topic("")
_TRIGGER_PREFIX = f"{trigger_wildcard().rsplit('/', 1)[0]}/"
_ACK_PREFIX = node_ack_topic("")


@dataclass
class HubRuntimeState:
    """In-memory snapshot of hub observability data."""

    last_seen: Dict[str, datetime] = field(default_factory=dict)

    def update_health(self, node_id: str, timestamp: datetime) -> None:
        """Record the last time a heartbeat was observed for a node."""
        self.last_seen[node_id] = timestamp

    def snapshot(self) -> Dict[str, float]:
        """Return seconds elapsed since the last heartbeat per node."""
        now = datetime.now(tz=timezone.utc)
        return {
            node_id: (now - seen).total_seconds()
            for node_id, seen in self.last_seen.items()
        }


class HubListener:
    """Coordinate MQTT communication between the hub and distributed nodes."""

    def __init__(
        self,
        config: HubConfig | None = None,
        mqtt_client: Optional[mqtt.Client] = None,
    ) -> None:
        if mqtt is None:
            raise RuntimeError("paho-mqtt must be installed to run the hub listener.")

        self._config = config or load_config()
        self._client = mqtt_client or mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._runtime = HubRuntimeState()
        self._narrative = NarrativeState(
            required_fragments=self._config.narrative.required_fragments_to_unlock,
        )
        self._event_logger = CsvEventLogger(self._config.logs_dir)

        self._ack_events: Dict[str, threading.Event] = {}
        self._ack_lock = threading.Lock()

    def start(self) -> None:
        """Connect to the MQTT broker and begin processing messages."""
        LOGGER.info(
            "Connecting to MQTT broker at %s:%s",
            self._config.broker_host,
            self._config.broker_port,
        )
        self._client.connect(self._config.broker_host, self._config.broker_port, keepalive=60)
        self._client.loop_start()

    def stop(self) -> None:
        """Stop the MQTT listener and close resources."""
        self._client.loop_stop()
        self._client.disconnect()
        self._event_logger.close()

    def run_forever(self) -> None:
        """Run the listener until interrupted."""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:  # pragma: no cover - manual stop
            LOGGER.info("Hub listener interrupted by user.")
            raise
        finally:
            self.stop()

    def push_node_config(
        self,
        node_id: str,
        payload: Dict[str, object],
        timeout: float = 5.0,
    ) -> bool:
        """Publish configuration updates to a node and await acknowledgement."""
        if not isinstance(payload, dict):
            raise ValueError("Node configuration payload must be a dictionary.")

        message = json.dumps(payload)
        ack_event = threading.Event()
        with self._ack_lock:
            self._ack_events[node_id] = ack_event

        info = self._client.publish(node_config_topic(node_id), message, qos=1)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:  # type: ignore[attr-defined]
            LOGGER.error("Failed to publish configuration to %s: rc=%s", node_id, info.rc)
            with self._ack_lock:
                self._ack_events.pop(node_id, None)
            return False

        LOGGER.info("Pushed configuration to %s, awaiting acknowledgement.", node_id)
        if ack_event.wait(timeout):
            self._event_logger.record_event("config_push_ok", node_id, message)
            return True

        LOGGER.warning("Configuration push to %s timed out after %.1fs.", node_id, timeout)
        self._event_logger.record_event("config_push_timeout", node_id, message)
        with self._ack_lock:
            self._ack_events.pop(node_id, None)
        return False

    def reset_state(self) -> None:
        """Clear the narrative state and retain heartbeat history."""
        self._narrative.reset()
        self.publish_state()
        self._event_logger.record_event("admin_action", "hub", "Narrative state reset")

    def get_state_snapshot(self) -> Dict[str, object]:
        """Return the current narrative state snapshot."""
        return self._narrative.snapshot()

    def get_health_snapshot(self) -> Dict[str, float]:
        """Return ages of the last heartbeat received per node."""
        return self._runtime.snapshot()

    def publish_state(self) -> None:
        """Publish the narrative state to the MQTT broker."""
        payload = json.dumps(self._narrative.snapshot())
        info = self._client.publish(hub_state_topic(), payload, qos=1, retain=True)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:  # type: ignore[attr-defined]
            LOGGER.error("Failed to publish hub state: rc=%s", info.rc)
        else:
            LOGGER.debug("Published hub state: %s", payload)

    # MQTT callbacks -----------------------------------------------------

    def _on_connect(
        self,
        client: mqtt.Client,
        _userdata: object,
        _flags: Dict[str, int],
        rc: int,
    ) -> None:
        if rc != 0:
            LOGGER.error("Failed to connect to MQTT broker (rc=%s).", rc)
            return
        LOGGER.info("Connected to MQTT broker.")
        client.subscribe(health_wildcard())
        client.subscribe(trigger_wildcard())
        client.subscribe(ack_wildcard())

    def _on_message(
        self,
        _client: mqtt.Client,
        _userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        topic = message.topic or ""
        payload = message.payload.decode("utf-8") if message.payload else ""
        if topic.startswith(_HEALTH_PREFIX):
            node_id = topic[len(_HEALTH_PREFIX) :]
            self._handle_health(node_id, payload)
        elif topic.startswith(_TRIGGER_PREFIX):
            node_id = topic[len(_TRIGGER_PREFIX) :]
            self._handle_trigger(node_id, payload)
        elif topic.startswith(_ACK_PREFIX):
            node_id = topic[len(_ACK_PREFIX) :]
            self._handle_ack(node_id, payload)
        else:
            LOGGER.debug("Ignoring message on unhandled topic: %s", topic)

    def _handle_health(self, node_id: str, payload: str) -> None:
        timestamp = datetime.now(tz=timezone.utc)
        try:
            data = json.loads(payload) if payload else {}
            epoch = data.get("ts")
            if isinstance(epoch, (int, float)):
                timestamp = datetime.fromtimestamp(epoch, tz=timezone.utc)
        except json.JSONDecodeError:
            LOGGER.warning("Invalid health payload from %s: %s", node_id, payload)
            self._event_logger.record_event("heartbeat_received", node_id, "invalid_json")
            return

        self._runtime.update_health(node_id, timestamp)
        self._event_logger.record_event("heartbeat_received", node_id, payload or "{}")

    def _handle_trigger(self, node_id: str, payload: str) -> None:
        try:
            data = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            LOGGER.warning("Invalid trigger payload from %s: %s", node_id, payload)
            self._event_logger.record_event("fragment_triggered", node_id, "invalid_json")
            return

        self._event_logger.record_event("fragment_triggered", node_id, json.dumps(data))

        unlocked_before = self._narrative.unlocked
        is_new = self._narrative.register_trigger(node_id)
        if not is_new:
            LOGGER.debug("Duplicate trigger received from %s; ignoring.", node_id)

        self.publish_state()
        unlocked_after = self._narrative.unlocked
        if unlocked_after and not unlocked_before:
            self._event_logger.record_event(
                "narrative_unlocked",
                node_id,
                "Unlock threshold reached",
            )
            LOGGER.info("Narrative unlocked after trigger from %s.", node_id)

    def _handle_ack(self, node_id: str, payload: str) -> None:
        self._event_logger.record_event("config_ack", node_id, payload or "{}")
        with self._ack_lock:
            event = self._ack_events.pop(node_id, None)
        if event:
            event.set()
        else:
            LOGGER.warning("Received unexpected ACK from %s.", node_id)


def run_forever() -> None:
    """Convenience entry point mirroring previous scaffold behaviour."""
    listener = HubListener()
    listener.run_forever()


__all__ = ["HubListener", "run_forever"]
