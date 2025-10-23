"""Minimal Flask dashboard application for the EchoTrace hub."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from flask import Flask, jsonify, render_template


TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_ROOT),
        static_folder=str(TEMPLATE_ROOT.parent / "static"),
    )

    @app.route("/health")
    def health() -> Dict[str, bool]:
        """Return a simple JSON response indicating the app is healthy."""
        return jsonify({"ok": True})

    @app.route("/")
    def index() -> str:
        """Render the dashboard landing page."""
        return render_template("index.html", title="EchoTrace Hub")

    return app


app: Optional[Flask] = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)  # type: ignore[union-attr]
