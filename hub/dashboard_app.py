"""Flask dashboard application serving the EchoTrace hub UI."""

from __future__ import annotations

import functools
import hmac
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, Response, abort, jsonify, redirect, render_template, request, send_file, url_for

from .accessibility_store import ACCESSIBILITY_PATH, apply_preset, load_profiles, save_profiles
from .config_loader import HubConfig, load_config
from .content_manager import ContentManager, ContentPack, MediaAsset
from .logging_utils import CsvEventLogger
from .narrative_state import NarrativeState


@dataclass
class DashboardContext:
    """Bundle services and state shared by dashboard routes."""

    config: HubConfig
    content_manager: ContentManager
    accessibility: Dict[str, Any]
    narrative_state: NarrativeState
    current_pack: Optional[ContentPack] = None
    health_snapshot: Dict[str, float] = field(default_factory=dict)

    def select_pack(self, pack_name: str) -> ContentPack:
        pack = self.content_manager.load_pack(pack_name)
        self.current_pack = pack
        return pack

    def reload_accessibility(self) -> None:
        self.accessibility = load_profiles(ACCESSIBILITY_PATH)


def create_app(config: HubConfig | None = None) -> Flask:
    """Create and configure the Flask application."""
    hub_config = config or load_config()

    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parent / "templates"),
        static_folder=str(Path(__file__).resolve().parent / "static"),
    )

    accessibility = load_profiles(ACCESSIBILITY_PATH)
    context = DashboardContext(
        config=hub_config,
        content_manager=ContentManager(),
        accessibility=accessibility,
        narrative_state=NarrativeState(
            required_fragments=hub_config.narrative.required_fragments_to_unlock
        ),
    )

    available_packs = context.content_manager.list_packs()
    if available_packs:
        try:
            context.select_pack(available_packs[0])
        except Exception as exc:  # pragma: no cover - defensive
            app.logger.warning("Failed to load initial pack '%s': %s", available_packs[0], exc)

    app.config["DASHBOARD_CONTEXT"] = context

    credentials: Optional[tuple[str, str]] = None
    if hub_config.security.require_basic_auth:
        username = os.getenv(hub_config.security.admin_user_env)
        password = os.getenv(hub_config.security.admin_pass_env)
        if not username or not password:
            raise RuntimeError(
                "Basic authentication is required but administrator credentials are not configured."
            )
        credentials = (username, password)
    app.config["ADMIN_CREDENTIALS"] = credentials

    def get_context() -> DashboardContext:
        return app.config["DASHBOARD_CONTEXT"]

    def require_auth(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            expected = app.config.get("ADMIN_CREDENTIALS")
            if not expected:
                return func(*args, **kwargs)
            auth = request.authorization
            if not auth:
                return _auth_required_response()
            if not (
                hmac.compare_digest(auth.username, expected[0])
                and hmac.compare_digest(auth.password, expected[1])
            ):
                return _auth_required_response()
            return func(*args, **kwargs)

        return wrapper

    @app.context_processor
    def inject_globals() -> Dict[str, Any]:
        ctx = get_context()
        accessibility_global = ctx.accessibility.get("global", {})
        return {
            "hub_config": ctx.config,
            "accessibility_profiles": ctx.accessibility,
            "accessibility_global": accessibility_global if isinstance(accessibility_global, dict) else {},
            "active_pack": ctx.current_pack,
        }

    # ------------------------------------------------------------------ Routes

    @app.route("/health")
    def health() -> Response:
        """Return a simple JSON response indicating the app is healthy."""
        return jsonify({"ok": True})

    @app.route("/")
    @require_auth
    def index() -> str:
        ctx = get_context()
        state = ctx.narrative_state.snapshot()
        return render_template(
            "index.html",
            state=state,
            active_pack=ctx.current_pack,
            available_packs=ctx.content_manager.list_packs(),
        )

    @app.route("/nodes")
    @require_auth
    def nodes() -> str:
        ctx = get_context()
        pack = ctx.current_pack
        nodes = pack.nodes if pack else {}
        health = ctx.health_snapshot
        assignments: Dict[str, MediaAsset] = {}
        if pack:
            for (node_id, lang), asset in pack.media.items():
                default_lang = nodes.get(node_id, {}).get("default_language")
                if default_lang == lang:
                    assignments[node_id] = asset
        return render_template(
            "nodes.html",
            nodes=nodes,
            health=health,
            assignments=assignments,
        )

    @app.route("/accessibility")
    @require_auth
    def accessibility_page() -> str:
        ctx = get_context()
        profiles = ctx.accessibility
        return render_template(
            "accessibility.html",
            profiles=profiles,
        )

    @app.route("/calibration")
    @require_auth
    def calibration() -> str:
        ctx = get_context()
        pack = ctx.current_pack
        nodes = pack.nodes if pack else {}
        return render_template("calibration.html", nodes=nodes)

    @app.route("/content")
    @require_auth
    def content() -> str:
        ctx = get_context()
        pack = ctx.current_pack
        all_packs = ctx.content_manager.list_packs()
        return render_template(
            "content.html",
            active_pack=pack,
            pack_names=all_packs,
        )

    @app.route("/analytics")
    @require_auth
    def analytics() -> str:
        ctx = get_context()
        state = ctx.narrative_state.snapshot()
        return render_template(
            "analytics.html",
            state=state,
            health=ctx.health_snapshot,
        )

    @app.route("/api/health")
    @require_auth
    def api_health() -> Response:
        ctx = get_context()
        return jsonify({"nodes": ctx.health_snapshot})

    @app.route("/api/state")
    @require_auth
    def api_state() -> Response:
        ctx = get_context()
        return jsonify(ctx.narrative_state.snapshot())

    @app.route("/api/reset-state", methods=["POST"])
    @require_auth
    def api_reset_state() -> Response:
        ctx = get_context()
        ctx.narrative_state.reset()
        return jsonify({"ok": True, "state": ctx.narrative_state.snapshot()})

    @app.route("/api/push-config", methods=["POST"])
    @require_auth
    def api_push_config() -> Response:
        ctx = get_context()
        data = _require_json(request)
        node_id = _require_field(data, "node_id")
        payload = data.get("payload")
        if not isinstance(payload, dict):
            abort(400, description="payload must be an object")
        app.logger.info("Configuration push requested for %s: %s", node_id, payload)
        # In this scaffold we acknowledge immediately. Future chunks will bridge to HubListener.
        return jsonify({"ok": True, "acknowledged": True, "node_id": node_id})

    @app.route("/api/apply-preset", methods=["POST"])
    @require_auth
    def api_apply_preset() -> Response:
        ctx = get_context()
        data = _require_json(request)
        preset_name = data.get("preset_name")
        profiles = ctx.accessibility

        if preset_name:
            try:
                apply_preset(profiles, preset_name)
            except KeyError as exc:
                abort(400, description=str(exc))
        elif "global" in data:
            global_settings = data["global"]
            if not isinstance(global_settings, dict):
                abort(400, description="global must be an object")
            profiles.setdefault("global", {}).update(global_settings)
        else:
            abort(400, description="Provide preset_name or global settings to apply.")

        save_profiles(profiles, ACCESSIBILITY_PATH)
        ctx.reload_accessibility()
        return jsonify({"ok": True, "global": ctx.accessibility.get("global", {})})

    @app.route("/api/select-pack", methods=["POST"])
    @require_auth
    def api_select_pack() -> Response:
        ctx = get_context()
        data = _require_json(request)
        pack_name = _require_field(data, "pack_name")
        try:
            pack = ctx.select_pack(pack_name)
        except FileNotFoundError:
            abort(404, description=f"Content pack '{pack_name}' not found.")
        except ValueError as exc:
            abort(400, description=str(exc))
        return jsonify({"ok": True, "pack": pack.name})

    @app.route("/api/export-csv")
    @require_auth
    def api_export_csv() -> Response:
        ctx = get_context()
        logger = CsvEventLogger(ctx.config.logs_dir)
        latest = logger.latest_csv()
        logger.close()
        if latest is None or not latest.exists():
            abort(404, description="No analytics CSV available yet.")
        return send_file(latest, mimetype="text/csv", as_attachment=True, download_name=latest.name)

    @app.route("/transcripts/<pack_name>/<path:filename>")
    def serve_transcript(pack_name: str, filename: str) -> Response:
        if Path(filename).suffix.lower() != ".html":
            abort(404)
        base_dir = (Path("content-packs") / pack_name / "transcripts").resolve()
        target_path = (base_dir / filename).resolve()
        if base_dir not in target_path.parents and target_path != base_dir:
            abort(404)
        if not target_path.exists():
            abort(404)
        return send_file(target_path, mimetype="text/html")

    @app.route("/logout")
    @require_auth
    def logout() -> Response:
        response = redirect(url_for("index"))
        response.headers["WWW-Authenticate"] = 'Basic realm="EchoTrace"'
        return response

    return app


def _auth_required_response() -> Response:
    response = Response(status=401)
    response.headers["WWW-Authenticate"] = 'Basic realm="EchoTrace"'
    return response


def _require_json(req) -> Dict[str, Any]:
    if not req.is_json:
        abort(400, description="Expected JSON body.")
    data = req.get_json()
    if not isinstance(data, dict):
        abort(400, description="JSON body must be an object.")
    return data


def _require_field(data: Dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not value or not isinstance(value, str):
        abort(400, description=f"Field '{field}' is required.")
    return value


app: Flask = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
