"""Smoke tests for the dashboard Flask application."""

from __future__ import annotations

from hub.dashboard_app import create_app


def test_health_endpoint_returns_ok() -> None:
    """Ensure the /health endpoint responds with a JSON payload."""
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
