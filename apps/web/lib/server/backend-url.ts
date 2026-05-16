import "server-only";

export function getBackendBaseUrl() {
  return (process.env.STOCK_API_BASE_URL ?? "http://localhost:8080").replace(/\/$/, "");
}

export function buildBackendUrl(path: string) {
  return `${getBackendBaseUrl()}/${path.replace(/^\//, "")}`;
}
