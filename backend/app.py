"""Flask application factory (design doc Section 6 architecture, Section 17
performance goals: parse fixtures once at startup and cache in memory).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from api.routes import api_bp
from certs.models import CertificateRecord, ParseError, PolicyFinding
from certs.normalize import build_certificate_records
from certs.policy import build_findings
from config import Config


@dataclass
class FixtureStore:
    """In-memory cache populated once at startup (Section 17: "Parse
    certificate fixtures once during startup", "Cache normalized certificate
    records in memory")."""

    records: list[CertificateRecord] = field(default_factory=list)
    parse_errors: list[ParseError] = field(default_factory=list)
    findings: list[PolicyFinding] = field(default_factory=list)
    load_error: str | None = None


def _configure_logging(level: str) -> None:
    # Structured logging per Section 18 -- one line per event, not print().
    logging.basicConfig(
        level=level,
        format='{"time":"%(asctime)s","level":"%(levelname)s",'
        '"logger":"%(name)s","message":"%(message)s"}',
    )


def _load_fixtures(config: Config, logger: logging.Logger) -> FixtureStore:
    store = FixtureStore()
    try:
        store.records, store.parse_errors = build_certificate_records(
            config.fixture_dir, config.reference_time, config.expiry_warning_days
        )
        store.findings = build_findings(store.records)
        logger.info(
            "Loaded %d certificate record(s), %d parse error(s), %d finding(s) from %s",
            len(store.records),
            len(store.parse_errors),
            len(store.findings),
            config.fixture_dir,
        )
        for err in store.parse_errors:
            logger.warning(
                "Fixture parse error (domain=%s, id=%s): %s", err.domain, err.fixture_id, err.reason
            )
    except Exception as exc:  # noqa: BLE001 - fail closed, surface via 500s instead of crashing
        store.load_error = str(exc)
        logger.error("Failed to load fixtures from %s: %s", config.fixture_dir, exc)
    return store


def create_app(config: Config | None = None) -> Flask:
    config = config or Config.from_env()
    _configure_logging(config.log_level)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    CORS(app, origins=config.cors_origins)

    app.config["APP_CONFIG"] = config
    app.config["FIXTURE_STORE"] = _load_fixtures(config, logger)
    app.register_blueprint(api_bp)

    @app.get("/healthz")
    def healthz():
        store = app.config["FIXTURE_STORE"]
        if store.load_error:
            return jsonify({"status": "error", "detail": store.load_error}), 500
        return jsonify({"status": "ok"})

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        code = (exc.name or "http_error").lower().replace(" ", "_")
        return jsonify({"error": {"code": code, "message": exc.description}}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        logger.exception("Unhandled exception")
        return (
            jsonify(
                {"error": {"code": "internal_error", "message": "An unexpected error occurred"}}
            ),
            500,
        )

    return app


if __name__ == "__main__":
    cfg = Config.from_env()
    application = create_app(cfg)
    application.run(host=cfg.api_host, port=cfg.api_port)
