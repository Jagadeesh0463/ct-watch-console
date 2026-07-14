// Highlights critical findings across all domains (design doc Section 14,
// Milestone 3 acceptance: "Critical findings visually highlighted").
export default function FindingsBanner({ findings }) {
  if (findings === null) {
    return null;
  }

  if (findings.length === 0) {
    return (
      <div className="findings-banner empty" data-testid="findings-banner">
        <h2>No critical findings</h2>
        <p style={{ margin: 0, fontSize: 13 }}>
          Every watched certificate currently passes expiry, chain, and pin checks.
        </p>
      </div>
    );
  }

  return (
    <div className="findings-banner" data-testid="findings-banner">
      <h2>
        {findings.length} critical finding{findings.length === 1 ? "" : "s"}
      </h2>
      <ul>
        {findings.map((f) => (
          <li key={`${f.certificate_id}-${f.rule}`} data-testid="critical-finding">
            <strong>{f.domain ?? f.certificate_id}</strong> &mdash; {f.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
