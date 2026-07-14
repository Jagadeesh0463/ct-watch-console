"""REST API routes (design doc Section 12: API Specification).

All error responses follow {"error": {"code": ..., "message": ...}} per the
doc. Endpoint-specific validation follows the doc's error column literally:
/api/certificates rejects any query param other than `domain` with 400;
/api/findings only validates the *value* of `severity` (an unrelated query
param is not documented as an error case there, so it's left alone).
"""

from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, request

from certs.models import Severity
from certs.serializers import finding_to_dict, record_to_dict

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _error(code: str, message: str, status: int) -> Response:
    response = jsonify({"error": {"code": code, "message": message}})
    response.status_code = status
    return response


def _store():
    return current_app.config["FIXTURE_STORE"]


def _fixture_load_error_response() -> Response | None:
    store = _store()
    if store.load_error:
        return _error("fixture_load_error", store.load_error, 500)
    return None


@api_bp.route("/domains", methods=["GET"])
def get_domains() -> Response:
    load_error = _fixture_load_error_response()
    if load_error is not None:
        return load_error
    store = _store()

    severity_rank = {Severity.CRITICAL: 2, Severity.WARNING: 1, Severity.INFO: 0}
    domains: dict[str, dict] = {}

    for record in store.records:
        if record.domain is None:
            continue
        domains.setdefault(
            record.domain, {"domain": record.domain, "cert_count": 0, "worst_severity": None}
        )
        domains[record.domain]["cert_count"] += 1

    for finding in store.findings:
        if finding.domain is None or finding.domain not in domains:
            continue
        entry = domains[finding.domain]
        current = entry["worst_severity"]
        if current is None or severity_rank[finding.severity] > severity_rank[Severity(current)]:
            entry["worst_severity"] = finding.severity.value

    return jsonify(list(domains.values()))


@api_bp.route("/certificates", methods=["GET"])
def get_certificates() -> Response:
    load_error = _fixture_load_error_response()
    if load_error is not None:
        return load_error
    store = _store()

    allowed_params = {"domain"}
    unknown = set(request.args.keys()) - allowed_params
    if unknown:
        return _error(
            "invalid_query_param",
            f"Unknown query parameter(s): {', '.join(sorted(unknown))}",
            400,
        )

    domain = request.args.get("domain")
    records = store.records
    if domain is not None:
        records = [r for r in records if r.domain == domain]

    return jsonify([record_to_dict(r) for r in records])


@api_bp.route("/certificates/<cert_id>", methods=["GET"])
def get_certificate(cert_id: str) -> Response:
    load_error = _fixture_load_error_response()
    if load_error is not None:
        return load_error
    store = _store()

    for record in store.records:
        if record.id == cert_id:
            return jsonify(record_to_dict(record))
    return _error("not_found", f"No certificate with id '{cert_id}'", 404)


@api_bp.route("/findings", methods=["GET"])
def get_findings() -> Response:
    load_error = _fixture_load_error_response()
    if load_error is not None:
        return load_error
    store = _store()

    findings = store.findings
    severity_param = request.args.get("severity")
    if severity_param is not None:
        try:
            severity = Severity(severity_param)
        except ValueError:
            valid = ", ".join(s.value for s in Severity)
            return _error(
                "invalid_severity",
                f"Invalid severity '{severity_param}'; expected one of: {valid}",
                400,
            )
        findings = [f for f in findings if f.severity == severity]

    return jsonify([finding_to_dict(f) for f in findings])
