import { useEffect, useMemo, useState } from "react";
import { ShieldCheck, AlertTriangle } from "lucide-react";
import DomainList from "./components/DomainList.jsx";
import FindingsBanner from "./components/FindingsBanner.jsx";
import CertificateDetail from "./components/CertificateDetail.jsx";
import StatCard from "./components/StatCard.jsx";
import { getDomains, getFindings, getCertificates } from "./api.js";

function formatScanTime(date) {
  if (!date) return null;
  const d = date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  const t = date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  });
  return `${d}, ${t} UTC`;
}

export default function App() {
  const [domains, setDomains] = useState([]);
  const [criticalFindings, setCriticalFindings] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [lastScan, setLastScan] = useState(null);

  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");

  const [selectedDomain, setSelectedDomain] = useState(null);
  const [certificates, setCertificates] = useState(null);
  const [selectedCertId, setSelectedCertId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getDomains(), getFindings("critical")])
      .then(([domainsRes, findingsRes]) => {
        if (cancelled) return;
        setDomains(domainsRes);
        setCriticalFindings(findingsRes);
        setLastScan(new Date());
      })
      .catch((err) => {
        if (cancelled) return;
        setLoadError(err.message ?? "Failed to load data from the API");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function handleSelectDomain(domain) {
    setSelectedDomain(domain);
    setCertificates(null);
    setSelectedCertId(null);
    getCertificates(domain)
      .then((records) => {
        setCertificates(records);
        setSelectedCertId(records[0]?.id ?? null);
      })
      .catch((err) => setLoadError(err.message ?? "Failed to load certificates"));
  }

  const stats = useMemo(() => {
    const totals = { total: domains.length, critical: 0, warning: 0, healthy: 0, certs: 0 };
    for (const d of domains) {
      if (d.worst_severity === "critical") totals.critical += 1;
      else if (d.worst_severity === "warning") totals.warning += 1;
      else totals.healthy += 1;
      totals.certs += d.cert_count ?? 0;
    }
    return totals;
  }, [domains]);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b border-border bg-bg/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-6 py-6">
          <div className="flex h-12 w-12 flex-none items-center justify-center rounded-xl bg-gradient-to-br from-primary to-blue-400 shadow-card-hover">
            <ShieldCheck className="h-6 w-6 text-white" strokeWidth={2.25} />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-[19px] font-bold tracking-tight text-white">
              CT Watch Console
            </h1>
            <p className="truncate text-[13px] text-muted">
              Monitor certificate health and policy findings across your infrastructure
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        {loadError && (
          <div className="mb-5 flex items-center gap-2 rounded-lg border border-critical/30 bg-critical-bg px-4 py-3 text-[13px] text-critical">
            <AlertTriangle className="h-4 w-4 flex-none" />
            {loadError}
          </div>
        )}

        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Total Domains" value={stats.total} tone="primary" />
          <StatCard label="Critical" value={stats.critical} tone="critical" />
          <StatCard label="Warning" value={stats.warning} tone="warning" />
          <StatCard label="Healthy" value={stats.healthy} tone="healthy" />
        </div>

        <FindingsBanner findings={criticalFindings} />

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)] lg:items-start">
          <DomainList
            domains={domains}
            search={search}
            onSearchChange={setSearch}
            severityFilter={severityFilter}
            onSeverityFilterChange={setSeverityFilter}
            selectedDomain={selectedDomain}
            onSelectDomain={handleSelectDomain}
          />
          <CertificateDetail
            domain={selectedDomain}
            certificates={certificates}
            selectedCertId={selectedCertId}
            onSelectCert={setSelectedCertId}
          />
        </div>
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-1.5 px-6 py-5 text-[11.5px] text-muted-soft sm:flex-row sm:items-center sm:justify-between">
          <span>{lastScan ? `Last scan ${formatScanTime(lastScan)}` : "Awaiting first scan…"}</span>
          <span>
            {stats.total} domain{stats.total === 1 ? "" : "s"} &middot; {stats.certs} certificate
            {stats.certs === 1 ? "" : "s"}
          </span>
        </div>
      </footer>
    </div>
  );
}
