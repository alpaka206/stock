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
        reason: "API URL이 설정되지 않아 기본 종목 구성을 표시합니다.",
      }),
    };
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "stocks");
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `stocks API 연결이 실패해 대체 종목 구성을 표시합니다. ${result.errorMessage}`,
      }),
    };
  }

  const payload = result.payload as Partial<StockApiResponse>;

  if (!payload.priceSeries?.length) {
    return {
      ...fallback,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "stocks API 응답에 가격 시계열이 없어 기본 종목 구성을 표시합니다.",
      }),
    };
  }

  return {
    instrument: payload.instrument ?? fallback.instrument,
    price: payload.latestPrice ?? fallback.price,
    changePercent: payload.changePercent ?? fallback.changePercent,
    thesis: payload.thesis ?? fallback.thesis,
    priceSeries: payload.priceSeries,
    eventMarkers: payload.eventMarkers ?? fallback.eventMarkers,
    indicatorGuides: payload.indicatorGuides ?? fallback.indicatorGuides,
    chartOverlays: payload.chartOverlays ?? fallback.chartOverlays,
    technicalMetrics: payload.technicalMetrics ?? fallback.technicalMetrics,
    patternCards: payload.patternCards ?? fallback.patternCards,
    rulePresetDefinitions: payload.rulePresetDefinitions ?? fallback.rulePresetDefinitions,
    scoreSummary: payload.scoreSummary ?? fallback.scoreSummary,
    flowMetrics: payload.flowMetrics ?? fallback.flowMetrics,
    flowUnavailable: payload.flowUnavailable ?? fallback.flowUnavailable,
    optionsShortMetrics: payload.optionsShortMetrics ?? fallback.optionsShortMetrics,
    optionsUnavailable: payload.optionsUnavailable ?? fallback.optionsUnavailable,
    issues: payload.issueCards ?? fallback.issues,
    relatedSymbols: payload.relatedSymbols ?? fallback.relatedSymbols,
    dataSource: buildPayloadDataSource(payload.sourceRefs ?? []),
  } satisfies StockFixture;
}
