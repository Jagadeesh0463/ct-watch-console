// Domain watchlist with search + severity filter (design doc Section 14,
// Milestone 3 acceptance: "Domain filter narrows list correctly").
function SeverityPill({ severity }) {
  const label = severity ?? "ok";
  return <span className={`severity-pill ${severity ?? "none"}`}>{label}</span>;
}

export default function DomainList({
  domains,
  search,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  selectedDomain,
  onSelectDomain,
}) {
  const filtered = domains.filter((d) => {
    const matchesSearch = d.domain.toLowerCase().includes(search.trim().toLowerCase());
    const matchesSeverity =
      severityFilter === "all" ? true : (d.worst_severity ?? "none") === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div>
      <div className="controls">
        <input
          type="text"
          placeholder="Search domains..."
          aria-label="Search domains"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          data-testid="domain-search"
        />
        <select
          aria-label="Filter by severity"
          value={severityFilter}
          onChange={(e) => onSeverityFilterChange(e.target.value)}
          data-testid="severity-filter"
        >
          <option value="all">All severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="none">OK</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">No domains match this filter.</div>
      ) : (
        <ul className="domain-list" data-testid="domain-list">
          {filtered.map((d) => (
            <li key={d.domain}>
              <button
                type="button"
                className={`domain-row ${d.domain === selectedDomain ? "selected" : ""}`}
                onClick={() => onSelectDomain(d.domain)}
                data-testid="domain-row"
              >
                <span className="domain-name">{d.domain}</span>
                <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ fontSize: 12, color: "#5c6470" }}>
                    {d.cert_count} cert{d.cert_count === 1 ? "" : "s"}
                  </span>
                  <SeverityPill severity={d.worst_severity} />
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
