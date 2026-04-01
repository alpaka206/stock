import "server-only";

const DEFAULT_RESEARCH_API_TIMEOUT_MS = 15000;

type FetchResearchApiJsonOptions = {
  explicitUrlEnv: string;
  basePath: string;
  pathSuffix?: string;
  query?: Record<string, string | undefined>;
};

export async function fetchResearchApiJson<TPayload>({
  explicitUrlEnv,
  basePath,
  pathSuffix,
  query,
}: FetchResearchApiJsonOptions) {
  const apiUrl = resolveResearchApiUrl({
    explicitUrlEnv,
    basePath,
    pathSuffix,
    query,
  });

  if (!apiUrl) {
    return null;
  }

  try {
    const requestInit: RequestInit = {
      headers: {
        Accept: "application/json",
      },
      next: {
        revalidate: 300,
      },
    };

    if (typeof AbortSignal.timeout === "function") {
      requestInit.signal = AbortSignal.timeout(DEFAULT_RESEARCH_API_TIMEOUT_MS);
    }

    const response = await fetch(apiUrl, requestInit);

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as TPayload;
  } catch {
    return null;
  }
}

function resolveResearchApiUrl({
  explicitUrlEnv,
  basePath,
  pathSuffix,
  query,
}: FetchResearchApiJsonOptions) {
  const explicitUrl = process.env[explicitUrlEnv]?.trim();
  const baseUrl =
    process.env.STOCK_API_BASE_URL?.trim() ??
    process.env.NEXT_PUBLIC_STOCK_API_BASE_URL?.trim();

  let resolvedUrl: string | null = null;

  if (explicitUrl) {
    resolvedUrl = buildUrlWithPath(explicitUrl, pathSuffix);
  } else if (baseUrl) {
    const root = `${baseUrl.replace(/\/$/, "")}/${basePath.replace(/^\//, "")}`;
    resolvedUrl = buildUrlWithPath(root, pathSuffix);
  }

  if (!resolvedUrl) {
    return null;
  }

  const url = new URL(resolvedUrl);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (!value) {
      return;
    }

    url.searchParams.set(key, value);
  });

  return url.toString();
}

function buildUrlWithPath(rawUrl: string, pathSuffix?: string) {
  if (!pathSuffix) {
    return rawUrl;
  }

  if (rawUrl.includes("{symbol}")) {
    return rawUrl.replace("{symbol}", encodeURIComponent(pathSuffix));
  }

  if (rawUrl.includes(":symbol")) {
    return rawUrl.replace(":symbol", encodeURIComponent(pathSuffix));
  }

  return `${rawUrl.replace(/\/$/, "")}/${encodeURIComponent(pathSuffix)}`;
}
