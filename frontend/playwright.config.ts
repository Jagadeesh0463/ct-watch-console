import { defineConfig, devices } from "@playwright/test";

// Runs against the real Flask backend, per design doc Section 9's rationale:
// fixture data is deterministic, so there is no need to mock the API. Both
// servers are started automatically for `npm run test:e2e`; REFERENCE_TIME is
// pinned to match the fixture generator's baked-in reference time so expiry
// statuses (expired/expiring-soon/valid) are exactly what the fixtures intend
// regardless of what day the suite actually runs.
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://localhost:4173",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "python3 app.py",
      cwd: "../backend",
      url: "http://localhost:5000/healthz",
      reuseExistingServer: !process.env.CI,
      env: { REFERENCE_TIME: "2026-07-14T00:00:00+00:00" },
      timeout: 30_000,
    },
    {
      command: "npm run preview",
      url: "http://localhost:4173",
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
