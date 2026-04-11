import "server-only";

import { buildHistoryFixture } from "@/dev/fixtures";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  assertResearchApiConfigured,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type { HistoryApiResponse, HistoryFixture } from "@/lib/research/types";

type HistoryReplayParams = {
  symbol?: string;
  range?: string;
  from?: string;
  to?: string;
};

export async function getHistoryReplay(params: HistoryReplayParams = {}) {
  const fallback = buildHistoryFixture(params.symbol);
  const result = await fetchResearchApiJson<HistoryApiResponse>({
    explicitUrlEnv: "HISTORY_API_URL",
    basePath: "/history",
    query: {
      symbol: params.symbol?.toUpperCase(),
      range: params.range,
      from: params.from,
      to: params.to,
    },
  });

  if (result.status === "disabled") {
    assertResearchApiConfigured(result, "history");
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 샘플 히스토리 리플레이를 표시합니다.",
      }),
    };
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "history");
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `history API 연결이 실패해 샘플 히스토리 리플레이를 대신 표시합니다. ${result.errorMessage}`,
      }),
    };
  }

  const payload = result.payload;

  if (!payload.priceSeries?.length || !payload.eventTimeline?.length) {
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "history API 응답에 차트 또는 이벤트 데이터가 부족해 샘플 히스토리 리플레이를 대신 표시합니다.",
      }),
    };
  }

  return {
    symbol: payload.symbol,
    range: payload.rangeLabel,
    availableRanges: payload.availableRanges,
    priceSeries: payload.priceSeries,
    eventMarkers: payload.eventMarkers,
    events: payload.eventTimeline,
    moveSummary: payload.moveSummary.text,
    moveReasons: payload.moveReasons,
    overlaps: payload.overlappingIndicators,
    dataSource: buildPayloadDataSource(payload.sourceRefs),
  } satisfies HistoryFixture;
}
