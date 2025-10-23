"""Logging utilities for EchoTrace hub services."""

from __future__ import annotations

import csv
import datetime as dt
import logging
from pathlib import Path
from typing import Optional, TextIO


LOGGER = logging.getLogger(__name__)

CSV_COLUMNS = ["timestamp", "event", "node_id", "detail"]


class CsvEventLogger:
    """Append EchoTrace events to a daily CSV file with automatic rotation."""

    def __init__(self, logs_dir: Path) -> None:
        self._logs_dir = logs_dir
        self._logs_dir.mkdir(parents=True, exist_ok=True)
        self._current_date: Optional[dt.date] = None
        self._file_path: Optional[Path] = None
        self._file_obj: Optional[TextIO] = None
        self._writer: Optional[csv.DictWriter] = None

    def record_event(self, event: str, node_id: Optional[str], detail: str) -> None:
        """Record a single event entry to the current CSV file."""
        timestamp = dt.datetime.now(tz=dt.timezone.utc)
        self._ensure_writer(timestamp.date())

        if self._writer is None:
            raise RuntimeError("CSV writer not initialised.")  # pragma: no cover

        row = {
            "timestamp": timestamp.isoformat(),
            "event": event,
            "node_id": node_id or "",
            "detail": detail,
        }

        try:
            self._writer.writerow(row)
            if self._file_obj:
                self._file_obj.flush()
        except OSError as exc:
            raise RuntimeError(f"Failed to write event log: {exc}") from exc

    def close(self) -> None:
        """Close the current file handle, if any."""
        if self._file_obj:
            try:
                self._file_obj.close()
            except OSError:
                LOGGER.debug("Failed to close event log file cleanly.", exc_info=True)
        self._file_obj = None
        self._writer = None
        self._current_date = None

    def latest_csv(self) -> Optional[Path]:
        """Return the most recent CSV file in the logs directory."""
        candidates = sorted(self._logs_dir.glob("*_events.csv"))
        if not candidates:
            return None
        return candidates[-1]

    def _ensure_writer(self, current_date: dt.date) -> None:
        if self._current_date == current_date and self._writer is not None:
            return
        self.close()

        filename = f"{current_date.isoformat()}_events.csv"
        file_path = self._logs_dir / filename

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_exists = file_path.exists()
            self._file_obj = file_path.open("a", encoding="utf-8", newline="")
            self._writer = csv.DictWriter(self._file_obj, fieldnames=CSV_COLUMNS)
            if not file_exists:
                self._writer.writeheader()
        except OSError as exc:
            raise RuntimeError(f"Unable to open log file {file_path}: {exc}") from exc

        self._current_date = current_date
        self._file_path = file_path

    def __del__(self) -> None:  # pragma: no cover - best-effort cleanup
        try:
            self.close()
        except Exception:
            LOGGER.debug("Error while closing CsvEventLogger during garbage collection.", exc_info=True)


__all__ = ["CsvEventLogger", "CSV_COLUMNS"]
