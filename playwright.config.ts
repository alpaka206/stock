import { defineConfig, devices } from "@playwright/test";

const port = Number(process.env.E2E_WEB_PORT ?? 3100);
const baseURL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: false,
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  reporter: [["list"]],
  use: {
    baseURL,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer:
    process.env.E2E_SKIP_WEB_SERVER === "true"
      ? undefined
      : {
          command: `pnpm --dir apps/web exec next dev --hostname 127.0.0.1 --port ${port}`,
          env: {
            NEXT_TELEMETRY_DISABLED: "1",
            OVERVIEW_API_TIMEOUT_MS: "1000",
            RESEARCH_ALLOW_FIXTURE_FALLBACK: "true",
            STOCK_API_BASE_URL: "",
          },
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          url: baseURL,
        },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
});
