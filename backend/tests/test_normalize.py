"""Integration tests over the generated sample fixtures (Milestone 1 acceptance criteria)."""

from __future__ import annotations

from certs.models import ExpiryStatus
from certs.normalize import build_certificate_records


def _by_id(records, cert_id):
    return next(r for r in records if r.id == cert_id)


def test_valid_domain_all_checks_pass(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    leaf = _by_id(records, "valid-leaf")
    assert leaf.expiry_status == ExpiryStatus.VALID
    assert leaf.hostname_match is True
    assert leaf.chain_valid is True
    assert leaf.spki_pin_match is True


def test_expired_leaf_flagged(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "expired-leaf").expiry_status == ExpiryStatus.EXPIRED


def test_expiring_soon_leaf_flagged(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "expiring-leaf").expiry_status == ExpiryStatus.EXPIRING_SOON


def test_hostname_mismatch_flagged(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "mismatch-leaf").hostname_match is False


def test_wildcard_hostname_match(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "wildcard-leaf").hostname_match is True


def test_broken_chain_missing_intermediate(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "broken-leaf").chain_valid is False


def test_pin_mismatch_flagged(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "pin-mismatch-leaf").spki_pin_match is False


def test_no_pin_configured_is_null(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    # expired.example.com never sets expected_spki_pins
    assert _by_id(records, "expired-leaf").spki_pin_match is None


def test_self_signed_root_only_chain_valid(fixture_dir, reference_time, warning_days):
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert _by_id(records, "selfsigned-leaf").chain_valid is True


def test_ca_certs_are_exempt_from_hostname_and_pin_checks(
    fixture_dir, reference_time, warning_days
):
    # Intermediate/root certs share a domain block with the leaf they signed,
    # but their own subject (e.g. "Root CA 1") never matches the watched
    # domain and their SPKI is never the pinned leaf key -- they must not be
    # penalized for either, or every domain with a CA chain would show
    # spurious hostname/pin findings caused only by its root and intermediate.
    records, _ = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    for cert_id in ("valid-root", "valid-intermediate"):
        record = _by_id(records, cert_id)
        assert record.hostname_match is True
        assert record.spki_pin_match is None


def test_malformed_entry_produces_parse_error_not_record(fixture_dir, reference_time, warning_days):
    records, errors = build_certificate_records(str(fixture_dir), reference_time, warning_days)
    assert not any(r.id == "malformed-cert" for r in records)
    assert any(e.fixture_id == "malformed-cert" for e in errors)


def test_malformed_fixture_file_is_skipped(tmp_path, reference_time, warning_days):
    (tmp_path / "broken.json").write_text("{not valid json")
    records, errors = build_certificate_records(str(tmp_path), reference_time, warning_days)
    assert records == []
    assert errors == []


def test_entry_missing_id_produces_parse_error(tmp_path, reference_time, warning_days):
    import json

    (tmp_path / "no_id.json").write_text(
        json.dumps(
            {
                "domains": [
                    {
                        "domain": "no-id.example.com",
                        "certificates": [{"pem": "irrelevant, id is checked first"}],
                    }
                ]
            }
        )
    )
    records, errors = build_certificate_records(str(tmp_path), reference_time, warning_days)
    assert records == []
    assert len(errors) == 1
    assert "id" in errors[0].reason


def test_entry_missing_pem_produces_parse_error(tmp_path, reference_time, warning_days):
    import json

    (tmp_path / "no_pem.json").write_text(
        json.dumps(
            {
                "domains": [
                    {
                        "domain": "no-pem.example.com",
                        "certificates": [{"id": "no-pem-cert"}],
                    }
                ]
            }
        )
    )
    records, errors = build_certificate_records(str(tmp_path), reference_time, warning_days)
    assert records == []
    assert any(e.fixture_id == "no-pem-cert" for e in errors)


def test_reproducibility_same_inputs_same_output(fixture_dir, reference_time, warning_days):
    args = (str(fixture_dir), reference_time, warning_days)
    first, first_errors = build_certificate_records(*args)
    second, second_errors = build_certificate_records(*args)
    assert first == second
    assert first_errors == second_errors
