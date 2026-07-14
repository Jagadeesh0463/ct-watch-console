// Certificate detail view for the selected domain (design doc Section 14,
// Milestone 3 acceptance: "Detail view shows correct certificate fields").
import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  MinusCircle,
  Fingerprint,
  FileText,
  Clock,
  Lock,
  Copy,
  Check,
  ShieldAlert,
  ShieldQuestion,
  ShieldCheck,
} from "lucide-react";

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function truncateHash(value) {
  if (!value || value.length <= 20) return value ?? "—";
  return `${value.slice(0, 10)}…${value.slice(-8)}`;
}

// Mirrors backend/certs/policy.py's severity mapping: expired / chain_broken /
// pin_mismatch = critical; expiring_soon / hostname_mismatch = warning.
function computeStatus(cert) {
  if (cert.expiry_status === "expired" || cert.chain_valid === false || cert.spki_pin_match === false) {
    return "critical";
  }
  if (cert.expiry_status === "expiring_soon" || cert.hostname_match === false) {
    return "warning";
  }
  return "healthy";
}

const STATUS_META = {
  critical: { label: "Critical", icon: ShieldAlert, cls: "text-critical bg-critical-bg border-critical/25" },
  warning: { label: "Warning", icon: ShieldQuestion, cls: "text-warning bg-warning-bg border-warning/25" },
  healthy: { label: "Healthy", icon: ShieldCheck, cls: "text-healthy bg-healthy-bg border-healthy/25" },
};

function SectionHeading({ icon: Icon, children }) {
  return (
    <div className="mt-5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-soft first:mt-0">
      <Icon className="h-3.5 w-3.5" />
      {children}
    </div>
  );
}

function OverviewRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2">
      <span className="text-[12.5px] text-muted">{label}</span>
      <span className="truncate text-[13px] font-medium text-text" title={typeof value === "string" ? value : undefined}>
        {value}
      </span>
    </div>
  );
}

function CheckRow({ label, value }) {
  const isUnknown = value === null || value === undefined;
  const Icon = isUnknown ? MinusCircle : value ? CheckCircle2 : XCircle;
  const cls = isUnknown ? "text-muted-soft" : value ? "text-healthy" : "text-critical";
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-[12.5px] text-muted">{label}</span>
      <span className={`flex items-center gap-1.5 text-[13px] font-medium ${cls}`}>
        <Icon className="h-4 w-4" strokeWidth={2.25} />
        {isUnknown ? "Not configured" : value ? "Pass" : "Fail"}
      </span>
    </div>
  );
}

function FingerprintRow({ label, value }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API unavailable (e.g. insecure context) -- fail silently,
      // the hash is still selectable/copyable by hand.
    }
  }

  return (
    <div className="py-2">
      <div className="mb-1 text-[12.5px] text-muted">{label}</div>
      <div className="flex items-center justify-between gap-2 rounded-md bg-bg px-2.5 py-1.5">
        <span className="select-all truncate font-mono text-[11.5px] text-muted" title={value ?? undefined}>
          {truncateHash(value)}
        </span>
        {value && (
          <button
            type="button"
            onClick={handleCopy}
            aria-label={`Copy ${label} fingerprint`}
            className="flex flex-none items-center gap-1 rounded px-1.5 py-0.5 text-[10.5px] text-muted-soft transition-colors hover:bg-surface-hover hover:text-text"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-healthy" /> Copied
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" /> Copy
              </>
            )}
          </button>
        )}
      </div>
    </div>
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
      <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-border bg-surface p-8 text-center text-[13px] text-muted-soft shadow-card">
        Select a domain to see its certificates.
      </div>
    );
  }

  if (certificates === null) {
    return (
      <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-border bg-surface p-8 text-center text-[13px] text-muted-soft shadow-card">
        Loading&hellip;
      </div>
    );
  }

  if (certificates.length === 0) {
    return (
      <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-border bg-surface p-8 text-center text-[13px] text-muted-soft shadow-card">
        No certificates found for {domain}.
      </div>
    );
  }

  const selected = certificates.find((c) => c.id === selectedCertId) ?? certificates[0];
  const status = computeStatus(selected);
  const { label: statusLabel, icon: StatusIcon, cls: statusCls } = STATUS_META[status];

  return (
    <div
      data-testid="certificate-detail"
      className="rounded-xl border border-border bg-surface p-5 shadow-card animate-fade-in"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="truncate text-[14px] font-semibold text-white">{domain}</h2>
        <span className={`flex flex-none items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11.5px] font-semibold ${statusCls}`}>
          <StatusIcon className="h-3.5 w-3.5" strokeWidth={2.25} />
          {statusLabel}
        </span>
      </div>

      {certificates.length > 1 && (
        <div className="mb-4 flex flex-wrap gap-1.5">
          {certificates.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => onSelectCert(c.id)}
              data-testid="cert-picker-button"
              className={`rounded-md border px-2.5 py-1 font-mono text-[11px] transition-colors ${
                c.id === selected.id
                  ? "border-primary bg-primary-bg text-primary"
                  : "border-border text-muted hover:border-border-hover hover:text-text"
              }`}
            >
              {c.id}
            </button>
          ))}
        </div>
      )}

      <SectionHeading icon={FileText}>Certificate</SectionHeading>
      <div className="mt-1 divide-y divide-border/70">
        <OverviewRow label="Subject" value={selected.subject} />
        <OverviewRow label="Issuer" value={selected.issuer} />
        <OverviewRow label="Hostnames" value={(selected.hostnames ?? []).join(", ") || "—"} />
      </div>

      <SectionHeading icon={Clock}>Validity</SectionHeading>
      <div className="mt-1 divide-y divide-border/70">
        <OverviewRow label="Not before" value={formatDate(selected.not_before)} />
        <OverviewRow label="Expires" value={formatDate(selected.not_after)} />
      </div>

      <SectionHeading icon={Lock}>Security Checks</SectionHeading>
      <div className="mt-1 divide-y divide-border/70">
        <CheckRow label="Hostname Match" value={selected.hostname_match} />
        <CheckRow label="Chain Valid" value={selected.chain_valid} />
        <CheckRow label="SPKI Pin Match" value={selected.spki_pin_match} />
      </div>

      <SectionHeading icon={Fingerprint}>Fingerprints</SectionHeading>
      <div className="mt-1 divide-y divide-border/70">
        <FingerprintRow label="SHA-256" value={selected.fingerprint_sha256} />
        <FingerprintRow label="SHA-1" value={selected.fingerprint_sha1} />
      </div>
    </div>
  );
}
