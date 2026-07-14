// Highlights critical findings across all domains (design doc Section 14,
// Milestone 3 acceptance: "Critical findings visually highlighted").
import { useState } from "react";
import { ShieldAlert, ShieldCheck, ChevronDown, ChevronUp } from "lucide-react";

export default function FindingsBanner({ findings }) {
  // Expanded by default so every "critical-finding" row is visible on first
  // render -- the Playwright suite asserts specific findings are visible
  // without interacting with a toggle first.
  const [expanded, setExpanded] = useState(true);

  if (findings === null) {
    return null;
  }

  if (findings.length === 0) {
    return (
      <div
        data-testid="findings-banner"
        className="relative mb-6 overflow-hidden rounded-lg border border-healthy/25 bg-healthy-bg py-3 pl-5 pr-4 shadow-card animate-fade-in"
      >
        <div className="absolute inset-y-0 left-0 w-1 bg-healthy" />
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="h-4 w-4 flex-none text-healthy" strokeWidth={2.25} />
          <span className="text-[13px] font-medium text-healthy">No critical findings</span>
          <span className="text-[12px] text-muted">
            &mdash; every watched certificate passes expiry, chain, and pin checks.
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="findings-banner"
      className="relative mb-6 overflow-hidden rounded-lg border border-critical/25 bg-critical-bg shadow-card animate-fade-in"
    >
      <div className="absolute inset-y-0 left-0 w-1 bg-critical" />
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between gap-2 px-5 py-3 text-left"
      >
        <span className="flex items-center gap-2 text-[13px] font-semibold text-critical">
          <ShieldAlert className="h-4 w-4" strokeWidth={2.25} />
          {findings.length} critical finding{findings.length === 1 ? "" : "s"}
        </span>
        {expanded ? (
          <ChevronUp className="h-3.5 w-3.5 flex-none text-critical/70" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5 flex-none text-critical/70" />
        )}
      </button>
      {expanded && (
        <ul className="flex flex-col gap-1.5 px-5 pb-4">
          {findings.map((f) => (
            <li
              key={`${f.certificate_id}-${f.rule}`}
              data-testid="critical-finding"
              className="rounded-md border border-critical/15 bg-bg/40 px-3 py-1.5 text-[12px] text-text"
            >
              <span className="font-semibold text-critical">{f.domain ?? f.certificate_id}</span>
              <span className="text-muted"> &mdash; {f.message}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
