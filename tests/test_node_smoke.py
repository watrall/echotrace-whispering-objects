"""Smoke tests for the node service scaffold."""

from __future__ import annotations

from pathlib import Path

from pi_nodes.node_service import NodeService


def test_node_service_run_once(tmp_path: Path) -> None:
    """NodeService.run_once should return a heartbeat-style payload."""
    config_path = tmp_path / "node_config.yaml"
    config_path.write_text("node_id: test-node\n", encoding="utf-8")

    service = NodeService(config_path=config_path)
    heartbeat = service.run_once()

    assert heartbeat["node_id"] == "test-node"
    assert "distance_mm" in heartbeat
    assert "timestamp" in heartbeat
