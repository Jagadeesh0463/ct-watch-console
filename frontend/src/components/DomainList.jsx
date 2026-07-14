// Domain watchlist with search + severity filter (design doc Section 14,
// Milestone 3 acceptance: "Domain filter narrows list correctly").
import { Search, ChevronDown, ChevronRight } from "lucide-react";

const SEVERITY_DOT = {
  critical: "bg-critical",
  warning: "bg-warning",
  none: "bg-healthy",
};

const SEVERITY_LABEL = {
  critical: "Critical",
  warning: "Warning",
  none: "Healthy",
};

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
    <div className="rounded-xl border border-border bg-surface shadow-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="text-[13px] font-semibold text-white">Domain Watchlist</h2>
        <span className="text-[11.5px] text-muted-soft">
          {filtered.length} of {domains.length}
        </span>
      </div>

      <div className="flex gap-2 border-b border-border p-3">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-soft" />
          <input
            type="text"
            placeholder="Search domains..."
            aria-label="Search domains"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            data-testid="domain-search"
            className="w-full rounded-lg border border-border bg-bg py-2 pl-8 pr-3 text-[13px] text-text placeholder:text-muted-soft transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/25"
          />
        </div>
        <div className="relative">
          <select
            aria-label="Filter by severity"
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            data-testid="severity-filter"
            className="h-full appearance-none rounded-lg border border-border bg-bg py-2 pl-3 pr-8 text-[13px] text-text transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/25"
          >
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="none">Healthy</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-soft" />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="px-4 py-10 text-center text-[13px] text-muted-soft">
          No domains match this filter.
        </div>
      ) : (
        <ul className="max-h-[560px] divide-y divide-border overflow-y-auto scrollbar-thin" data-testid="domain-list">
          {filtered.map((d) => {
            const severity = d.worst_severity ?? "none";
            const isSelected = d.domain === selectedDomain;
            return (
              <li key={d.domain}>
                <button
                  type="button"
                  onClick={() => onSelectDomain(d.domain)}
                  data-testid="domain-row"
                  className={`group flex w-full items-center gap-3 px-4 py-3.5 text-left transition-colors ${
                    isSelected ? "bg-primary-bg" : "hover:bg-surface-hover"
                  }`}
                >
                  <span className={`h-2 w-2 flex-none rounded-full ${SEVERITY_DOT[severity]}`} />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[13.5px] font-medium text-white">
                      {d.domain}
                    </span>
                    <span className="mt-0.5 flex items-center gap-2 text-[11.5px] text-muted">
                      <span>
                        {d.cert_count} cert{d.cert_count === 1 ? "" : "s"}
                      </span>
                      <span className="text-muted-soft">&middot;</span>
                      <span>{SEVERITY_LABEL[severity]}</span>
                    </span>
                  </span>
                  <ChevronRight
                    className={`h-4 w-4 flex-none text-muted-soft transition-transform ${
                      isSelected ? "translate-x-0.5 text-primary" : "group-hover:translate-x-0.5"
                    }`}
                  />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
