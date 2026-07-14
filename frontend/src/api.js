// Thin client for the Flask API (design doc Section 12). Defaults to
// http://localhost:5000 for local dev/e2e; override via VITE_API_BASE_URL at
// build time (used by the Docker frontend image to point at the compose
// backend service).
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

class ApiError extends Error {
  constructor(code, message, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request(path) {
  const res = await fetch(`${API_BASE}${path}`);
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const err = body?.error ?? { code: "unknown_error", message: res.statusText };
    throw new ApiError(err.code, err.message, res.status);
  }
  return body;
}

export function getDomains() {
  return request("/api/domains");
}

export function getCertificates(domain) {
  const query = domain ? `?domain=${encodeURIComponent(domain)}` : "";
  return request(`/api/certificates${query}`);
}

export function getCertificate(id) {
  return request(`/api/certificates/${encodeURIComponent(id)}`);
}

export function getFindings(severity) {
  const query = severity ? `?severity=${encodeURIComponent(severity)}` : "";
  return request(`/api/findings${query}`);
}

export { ApiError };
