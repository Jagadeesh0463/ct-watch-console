// Certificate detail view for the selected domain (design doc Section 14,
// Milestone 3 acceptance: "Detail view shows correct certificate fields").
function Field({ label, value }) {
  return (
    <>
      <dt>{label}</dt>
      <dd>{value === null || value === undefined || value === "" ? "—" : String(value)}</dd>
    </>
  );
}

export default function CertificateDetail({
  domain,
  certificates,
  selectedCertId,
  onSelectCert,
}) {
  if (!domain) {
    return (
      <div className="detail-panel">
        <h2>Certificate detail</h2>
        <div className="empty-state">Select a domain to see its certificates.</div>
      </div>
    );
  }

  if (certificates === null) {
    return (
      <div className="detail-panel">
        <h2>Certificate detail</h2>
        <div className="empty-state">Loading...</div>
      </div>
    );
  }

  if (certificates.length === 0) {
    return (
      <div className="detail-panel">
        <h2>Certificate detail</h2>
        <div className="empty-state">No certificates found for {domain}.</div>
      </div>
    );
  }

  const selected = certificates.find((c) => c.id === selectedCertId) ?? certificates[0];

  return (
    <div className="detail-panel" data-testid="certificate-detail">
      <h2>{domain}</h2>
      {certificates.length > 1 && (
        <div className="cert-picker">
          {certificates.map((c) => (
            <button
              key={c.id}
              type="button"
              className={c.id === selected.id ? "selected" : ""}
              onClick={() => onSelectCert(c.id)}
              data-testid="cert-picker-button"
            >
              {c.id}
            </button>
          ))}
        </div>
      )}
      <dl className="cert-fields">
        <Field label="ID" value={selected.id} />
        <Field label="Subject" value={selected.subject} />
        <Field label="Issuer" value={selected.issuer} />
        <Field label="SHA-256 fingerprint" value={selected.fingerprint_sha256} />
        <Field label="SHA-1 fingerprint" value={selected.fingerprint_sha1} />
        <Field label="Not before" value={selected.not_before} />
        <Field label="Not after" value={selected.not_after} />
        <Field label="Expiry status" value={selected.expiry_status} />
        <Field label="Hostnames" value={(selected.hostnames ?? []).join(", ")} />
        <Field label="Hostname match" value={String(selected.hostname_match)} />
        <Field label="Chain valid" value={String(selected.chain_valid)} />
        <Field
          label="SPKI pin match"
          value={selected.spki_pin_match === null ? "not configured" : String(selected.spki_pin_match)}
        />
      </dl>
    </div>
  );
}
