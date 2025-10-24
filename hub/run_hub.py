"""Supervisory launcher for the EchoTrace hub services."""

from __future__ import annotations

import logging
import signal
import sys
from contextlib import suppress

try:
    from waitress import serve  # type: ignore[import]
except ImportError:  # pragma: no cover - fallback for development
    serve = None  # type: ignore[assignment]

from .config_loader import HubConfig, load_config
from .dashboard_app import create_app
from .hub_listener import HubListener


LOGGER = logging.getLogger(__name__)
HUB_LISTENER: HubListener | None = None


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def run_server(config: HubConfig) -> None:
    """Run the Flask dashboard with Waitress when available."""
    if HUB_LISTENER is None:
        raise RuntimeError("Hub listener not initialised.")
    app = create_app(config=config, hub_controller=HUB_LISTENER)
    if serve is not None:
        serve(app, host=config.dashboard_host, port=config.dashboard_port)
    else:  # pragma: no cover - fallback for local use without waitress
        LOGGER.warning("Waitress not installed; using Flask development server.")
        app.run(host=config.dashboard_host, port=config.dashboard_port)


def main() -> None:
    """Entry point used by systemd to start the hub stack."""
    _configure_logging()

    config = load_config()
    global HUB_LISTENER  # type: ignore[global-variable-not-assigned]
    HUB_LISTENER = HubListener(config=config)
    HUB_LISTENER.start()
    LOGGER.info(
        "Hub listener initialised; launching dashboard on %s:%s",
        config.dashboard_host,
        config.dashboard_port,
    )

    def shutdown_handler(_signum: int, _frame: object | None) -> None:
        LOGGER.info("Shutdown signal received; stopping services.")
        HUB_LISTENER.stop()
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(ValueError):
            signal.signal(sig, shutdown_handler)

    try:
        run_server(config)
    finally:
        if HUB_LISTENER is not None:
            HUB_LISTENER.stop()


if __name__ == "__main__":  # pragma: no cover - script execution
    main()
