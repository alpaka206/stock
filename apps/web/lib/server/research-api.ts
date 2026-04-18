import "server-only";

import type { ResearchDataSource, SourceRef } from "@/lib/research/types";

const DEFAULT_RESEARCH_API_TIMEOUT_MS = 15000;
const RELEASE_REMOTE_RESEARCH_API_MIN_TIMEOUT_MS = 30000;
const RESEARCH_FIXTURE_FALLBACK_ENV = "RESEARCH_ALLOW_FIXTURE_FALLBACK";

type FetchResearchApiJsonOptions = {
  explicitUrlEnv: string;
  basePath: string;
  pathSuffix?: string;
  query?: Record<string, string | undefined>;
  timeoutMs?: number;
};

export type ResearchApiFetchResult<TPayload> =
  | {
      status: "disabled";
      payload: null;
      apiUrl: null;
      errorMessage: null;
    }
  | {
      status: "success";
      payload: TPayload;
      apiUrl: string;
      errorMessage: null;
    }
  | {
      status: "error";
      payload: null;
      apiUrl: string;
      errorMessage: string;
    };

export async function fetchResearchApiJson<TPayload>({
  explicitUrlEnv,
  basePath,
  pathSuffix,
  query,
  timeoutMs = DEFAULT_RESEARCH_API_TIMEOUT_MS,
}: FetchResearchApiJsonOptions) {
  const apiUrl = resolveResearchApiUrl({
    explicitUrlEnv,
    basePath,
    pathSuffix,
    query,
  });

  if (!apiUrl) {
    return {
      status: "disabled",
      payload: null,
      apiUrl: null,
      errorMessage: null,
    } satisfies ResearchApiFetchResult<TPayload>;
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
    const effectiveTimeoutMs = getEffectiveResearchApiTimeoutMs(timeoutMs, apiUrl);

    if (effectiveTimeoutMs > 0 && typeof AbortSignal.timeout === "function") {
      requestInit.signal = AbortSignal.timeout(effectiveTimeoutMs);
    }

    const response = await fetch(apiUrl, requestInit);

    if (!response.ok) {
      return {
        status: "error",
        payload: null,
        apiUrl,
        errorMessage: `API 응답이 ${response.status} 상태로 실패했습니다.`,
      } satisfies ResearchApiFetchResult<TPayload>;
    }

    return {
      status: "success",
      payload: (await response.json()) as TPayload,
      apiUrl,
      errorMessage: null,
    } satisfies ResearchApiFetchResult<TPayload>;
  } catch (error) {
    return {
      status: "error",
      payload: null,
      apiUrl,
      errorMessage:
        error instanceof Error
          ? `API 요청이 실패했습니다: ${error.message}`
          : "API 요청이 실패했습니다.",
    } satisfies ResearchApiFetchResult<TPayload>;
  }
}

export function allowFixtureFallback() {
  const configuredValue = process.env[RESEARCH_FIXTURE_FALLBACK_ENV]?.trim().toLowerCase();

  if (configuredValue === "true") {
    return true;
  }

  if (configuredValue === "false") {
    return false;
  }

  return process.env.NODE_ENV !== "production";
}

function isFixtureFallbackLocked() {
  return process.env[RESEARCH_FIXTURE_FALLBACK_ENV]?.trim().toLowerCase() === "false";
}

export function buildFixtureDataSource({
  reason,
  fallback,
}: {
  reason: string;
  fallback: boolean;
}): ResearchDataSource {
  return fallback
    ? {
        mode: "fixture-fallback",
        label: "대체 데이터",
        description: reason,
      }
    : {
        mode: "fixture",
        label: "기본 데이터",
        description: reason,
      };
}

export function buildPayloadDataSource(sourceRefs: SourceRef[]): ResearchDataSource {
  const isMockPayload =
    sourceRefs.length > 0 && sourceRefs.every((sourceRef) => sourceRef.kind === "mock");

  if (isMockPayload) {
    return {
      mode: "mock",
      label: "검증 응답",
      description: "API가 검증용 sourceRefs를 반환했습니다. 실제 분석용 데이터로 사용하지 마세요.",
    };
  }

  return {
    mode: "live",
    label: "실시간 데이터",
    description: "연결된 sourceRefs와 결정론적 계산 결과를 기준으로 화면을 구성했습니다.",
  };
}

export function assertResearchApiAvailable(result: ResearchApiFetchResult<unknown>, pageLabel: string) {
  if (result.status !== "error" || !isFixtureFallbackLocked()) {
    return;
  }

  throw new Error(
    `${pageLabel} API 연결이 실패했습니다. release 모드에서는 대체 데이터를 자동 표시하지 않습니다. ${result.errorMessage}`
  );
}

export function assertResearchApiConfigured(
  result: ResearchApiFetchResult<unknown>,
  pageLabel: string
) {
  if (result.status !== "disabled" || !isFixtureFallbackLocked()) {
    return;
  }

  throw new Error(
    `${pageLabel} API URL이 설정되지 않았습니다. release 모드에서는 fixture fallback을 허용하지 않습니다. STOCK_API_BASE_URL 또는 route별 API URL을 설정해야 합니다.`
  );
}

function resolveResearchApiUrl({
  explicitUrlEnv,
  basePath,
  pathSuffix,
  query,
}: FetchResearchApiJsonOptions) {
  const explicitUrl = process.env[explicitUrlEnv]?.trim();
  const baseUrl = process.env.STOCK_API_BASE_URL?.trim();

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

function getEffectiveResearchApiTimeoutMs(timeoutMs: number, apiUrl: string) {
  if (timeoutMs <= 0) {
    return timeoutMs;
  }

  if (!isFixtureFallbackLocked()) {
    return timeoutMs;
  }

  if (isLocalResearchApiUrl(apiUrl)) {
    return timeoutMs;
  }

  return Math.max(timeoutMs, RELEASE_REMOTE_RESEARCH_API_MIN_TIMEOUT_MS);
}

function isLocalResearchApiUrl(apiUrl: string) {
  const hostname = new URL(apiUrl).hostname.trim().toLowerCase();

  return (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "[::1]" ||
    hostname === "::1" ||
    hostname === "0.0.0.0"
  );
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
