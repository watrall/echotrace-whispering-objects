"""Tests for analytics summarisation utilities."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hub.logging_utils import summarize_events


def _write_log(log_path: Path) -> None:
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "event", "node_id", "detail"])
        writer.writeheader()
        base_time = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        writer.writerow(
            {
                "timestamp": base_time.isoformat(),
                "event": "fragment_triggered",
                "node_id": "object1",
                "detail": "{}",
            }
        )
        writer.writerow(
            {
                "timestamp": (base_time + timedelta(seconds=30)).isoformat(),
                "event": "fragment_triggered",
                "node_id": "object1",
                "detail": "{}",
            }
        )
        writer.writerow(
            {
                "timestamp": base_time.isoformat(),
                "event": "heartbeat_received",
                "node_id": "object1",
                "detail": "{}",
            }
        )
        writer.writerow(
            {
                "timestamp": base_time.isoformat(),
                "event": "narrative_unlocked",
                "node_id": "mystery",
                "detail": "{}",
            }
        )


def test_summarize_events(tmp_path: Path) -> None:
    """Summary should aggregate counts and compute intervals."""
    log_path = tmp_path / "2025-01-01_events.csv"
    _write_log(log_path)

    summary = summarize_events(tmp_path)
    assert summary is not None
    assert summary.by_node["object1"] == 2
    assert summary.heartbeat_by_node["object1"] == 1
    assert summary.narrative_unlocks == 1
    assert summary.total_triggers == 2
    assert 0.4 <= summary.completion_rate <= 1.0
    assert summary.mean_trigger_interval_seconds == 30
    assert summary.recent_events, "Expected recent events to be populated."
