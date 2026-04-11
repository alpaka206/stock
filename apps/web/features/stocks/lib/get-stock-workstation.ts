import "server-only";

import { buildStockFixture } from "@/dev/fixtures";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  assertResearchApiConfigured,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type { StockApiResponse, StockFixture } from "@/lib/research/types";

export async function getStockWorkstation(symbol: string) {
  const fallback = buildStockFixture(symbol);
  const result = await fetchResearchApiJson<StockApiResponse>({
    explicitUrlEnv: "STOCK_DETAIL_API_URL",
    basePath: "/stocks",
    pathSuffix: symbol.toUpperCase(),
  });

  if (result.status === "disabled") {
    assertResearchApiConfigured(result, "stocks");
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 샘플 종목 워크스테이션을 표시합니다.",
      }),
    };
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "stocks");
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `stocks API 연결이 실패해 샘플 종목 워크스테이션을 대신 표시합니다. ${result.errorMessage}`,
      }),
    };
  }

  const payload = result.payload;

  if (!payload.priceSeries?.length) {
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "stocks API 응답에 가격 시계열이 없어 샘플 종목 워크스테이션을 대신 표시합니다.",
      }),
    };
  }

  return {
    instrument: payload.instrument,
    price: payload.latestPrice,
    changePercent: payload.changePercent,
    thesis: payload.thesis,
    priceSeries: payload.priceSeries,
    eventMarkers: payload.eventMarkers,
    indicatorGuides: payload.indicatorGuides,
    rulePresetDefinitions: payload.rulePresetDefinitions,
    scoreSummary: payload.scoreSummary,
    flowMetrics: payload.flowMetrics,
    flowUnavailable: payload.flowUnavailable,
    optionsShortMetrics: payload.optionsShortMetrics,
    optionsUnavailable: payload.optionsUnavailable,
    issues: payload.issueCards,
    relatedSymbols: payload.relatedSymbols,
    dataSource: buildPayloadDataSource(payload.sourceRefs),
  } satisfies StockFixture;
}
