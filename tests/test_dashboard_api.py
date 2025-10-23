"""Integration tests for authenticated dashboard endpoints."""

from __future__ import annotations

import os

os.environ.setdefault("ECHOTRACE_ADMIN_USER", "admin")
os.environ.setdefault("ECHOTRACE_ADMIN_PASS", "secret")

import base64

import pytest

from hub.dashboard_app import create_app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as testing_client:
        yield testing_client


def _auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin:secret").decode("utf-8")
    return {"Authorization": f"Basic {token}"}


def test_overview_requires_auth(client) -> None:
    """Ensure unauthenticated access is blocked."""
    response = client.get("/")
    assert response.status_code == 401

    authed = client.get("/", headers=_auth_header())
    assert authed.status_code == 200
    assert b"Installation Snapshot" in authed.data


def test_api_state_and_reset(client) -> None:
    """Check narrative state JSON surfaces and resets."""
    state_resp = client.get("/api/state", headers=_auth_header())
    assert state_resp.status_code == 200
    payload = state_resp.get_json()
    assert "unlocked" in payload
    assert "triggered" in payload

    reset_resp = client.post("/api/reset-state", headers=_auth_header())
    assert reset_resp.status_code == 200
    reset_payload = reset_resp.get_json()
    assert reset_payload["ok"] is True
