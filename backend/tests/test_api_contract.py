"""API contract tests (design doc Section 12), Flask test client, in-process.

Exercises every endpoint against the same generated sample fixtures used by
the Milestone 1 tests, both happy and error paths, per the doc's Testing
Strategy table (Section 20: "Contract | pytest + Flask test client | every
API endpoint, every fixture domain | 100% of endpoints, both happy and error
paths").
"""

from __future__ import annotations


def test_healthz_ok(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_get_domains_shape_and_content(client):
    resp = client.get("/api/domains")
    assert resp.status_code == 200
    domains = resp.get_json()
    assert isinstance(domains, list)
    by_name = {d["domain"]: d for d in domains}

    assert "valid.example.com" in by_name
    assert by_name["valid.example.com"]["cert_count"] >= 1
    assert by_name["valid.example.com"]["worst_severity"] is None

    assert by_name["expired.example.com"]["worst_severity"] == "critical"
    assert by_name["broken-chain.example.com"]["worst_severity"] == "critical"
    assert by_name["expiring-soon.example.com"]["worst_severity"] == "warning"


def test_get_certificates_returns_all_records(client):
    resp = client.get("/api/certificates")
    assert resp.status_code == 200
    records = resp.get_json()
    assert isinstance(records, list)
    assert any(r["id"] == "valid-leaf" for r in records)


def test_get_certificates_domain_filter(client):
    resp = client.get("/api/certificates?domain=expired.example.com")
    assert resp.status_code == 200
    records = resp.get_json()
    assert records and all(r["domain"] == "expired.example.com" for r in records)


def test_get_certificates_unknown_filter_param_is_400(client):
    resp = client.get("/api/certificates?bogus=1")
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "invalid_query_param"


def test_get_certificate_by_id(client):
    resp = client.get("/api/certificates/valid-leaf")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == "valid-leaf"


def test_get_certificate_by_id_not_found(client):
    resp = client.get("/api/certificates/does-not-exist")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"]["code"] == "not_found"


def test_get_findings_returns_all(client):
    resp = client.get("/api/findings")
    assert resp.status_code == 200
    findings = resp.get_json()
    assert isinstance(findings, list)
    assert any(f["certificate_id"] == "expired-leaf" and f["rule"] == "expired" for f in findings)


def test_get_findings_severity_filter(client):
    resp = client.get("/api/findings?severity=critical")
    assert resp.status_code == 200
    findings = resp.get_json()
    assert findings and all(f["severity"] == "critical" for f in findings)


def test_get_findings_invalid_severity_is_400(client):
    resp = client.get("/api/findings?severity=nonsense")
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "invalid_severity"


def test_unmatched_route_is_404_with_error_shape(client):
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404
    body = resp.get_json()
    assert "error" in body and "code" in body["error"]


def test_get_domains_ignores_records_and_findings_with_no_domain(app, client):
    from certs.models import CertificateRecord, ExpiryStatus, PolicyFinding, Rule, Severity

    store = app.config["FIXTURE_STORE"]
    store.records.append(
        CertificateRecord(
            id="no-domain-cert",
            domain=None,
            subject="CN=orphan",
            issuer="CN=orphan",
            fingerprint_sha256="0" * 64,
            fingerprint_sha1="0" * 40,
            not_before=None,
            not_after=None,
            expiry_status=ExpiryStatus.VALID,
            hostnames=[],
            hostname_match=True,
            chain_valid=True,
            spki_pin_match=None,
        )
    )
    store.findings.append(
        PolicyFinding(
            domain=None,
            certificate_id="no-domain-cert",
            rule=Rule.CHAIN_BROKEN,
            severity=Severity.CRITICAL,
            message="orphan finding with no domain",
        )
    )

    resp = client.get("/api/domains")
    assert resp.status_code == 200
    assert not any(d["domain"] is None for d in resp.get_json())


def test_unhandled_exception_returns_generic_500(monkeypatch, client):
    import api.routes as routes_module

    def _boom(_record):
        raise RuntimeError("boom, should not leak to the client")

    monkeypatch.setattr(routes_module, "record_to_dict", _boom)

    resp = client.get("/api/certificates")
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["error"]["code"] == "internal_error"
    assert "boom" not in body["error"]["message"]


def test_fixture_load_failure_surfaces_as_500(monkeypatch, reference_time, warning_days):
    import app as app_module
    from config import Config

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated fixture load failure")

    monkeypatch.setattr(app_module, "build_certificate_records", _boom)

    config = Config(
        fixture_dir="irrelevant", expiry_warning_days=warning_days, reference_time=reference_time
    )
    flask_app = app_module.create_app(config)
    client = flask_app.test_client()

    resp = client.get("/api/domains")
    assert resp.status_code == 500
    assert resp.get_json()["error"]["code"] == "fixture_load_error"

    resp = client.get("/api/certificates")
    assert resp.status_code == 500

    resp = client.get("/api/findings")
    assert resp.status_code == 500

    resp = client.get("/api/certificates/anything")
    assert resp.status_code == 500

    resp = client.get("/healthz")
    assert resp.status_code == 500
