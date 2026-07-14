import { useEffect, useState } from "react";
import DomainList from "./components/DomainList.jsx";
import FindingsBanner from "./components/FindingsBanner.jsx";
import CertificateDetail from "./components/CertificateDetail.jsx";
import { getDomains, getFindings, getCertificates } from "./api.js";

export default function App() {
  const [domains, setDomains] = useState([]);
  const [criticalFindings, setCriticalFindings] = useState(null);
  const [loadError, setLoadError] = useState(null);

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

  return (
    <div className="app">
      <header className="app-header">
        <h1>Certificate Transparency Watch Console</h1>
        <p>Watchlist of monitored domains and their certificate policy findings.</p>
      </header>

      {loadError && <div className="status-line error">{loadError}</div>}

      <FindingsBanner findings={criticalFindings} />

      <div className="layout">
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
    </div>
  );
}
