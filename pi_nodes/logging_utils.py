"""Logging helpers for EchoTrace node processes."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_node_logging(log_file: Path = Path("node.log")) -> None:
    """Configure logging to emit to stdout and to a rotating log file."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(_default_formatter())

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=512_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(_default_formatter())

    root.addHandler(stream_handler)
    root.addHandler(file_handler)


def _default_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


__all__ = ["configure_node_logging"]
