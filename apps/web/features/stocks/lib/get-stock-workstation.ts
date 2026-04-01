import "server-only";

import { buildStockFixture } from "@/dev/fixtures";
import { fetchResearchApiJson } from "@/lib/server/research-api";
import type { AvailabilityState, StockFixture } from "@/lib/research/types";

type StockApiResponse = {
  instrument?: StockFixture["instrument"];
  latestPrice?: number;
  changePercent?: number;
  thesis?: string;
  priceSeries?: StockFixture["priceSeries"];
  eventMarkers?: StockFixture["eventMarkers"];
  indicatorGuides?: StockFixture["indicatorGuides"];
  rulePresetDefinitions?: StockFixture["rulePresetDefinitions"];
  scoreSummary?: StockFixture["scoreSummary"];
  flowMetrics?: StockFixture["flowMetrics"];
  flowUnavailable?: AvailabilityState;
  optionsShortMetrics?: StockFixture["optionsShortMetrics"];
  optionsUnavailable?: AvailabilityState;
  issueCards?: StockFixture["issues"];
  relatedSymbols?: string[];
};

export async function getStockWorkstation(symbol: string) {
  const fallback = buildStockFixture(symbol);
  const payload = await fetchResearchApiJson<StockApiResponse>({
    explicitUrlEnv: "STOCK_DETAIL_API_URL",
    basePath: "/stocks",
    pathSuffix: symbol.toUpperCase(),
  });

  if (!payload?.instrument || !payload.priceSeries?.length) {
    return fallback;
  }

  return {
    instrument: payload.instrument,
    price: payload.latestPrice ?? fallback.price,
    changePercent: payload.changePercent ?? fallback.changePercent,
    thesis: payload.thesis ?? fallback.thesis,
    priceSeries: payload.priceSeries,
    eventMarkers: payload.eventMarkers ?? [],
    indicatorGuides: payload.indicatorGuides ?? [],
    rulePresetDefinitions:
      payload.rulePresetDefinitions ?? fallback.rulePresetDefinitions,
    scoreSummary: payload.scoreSummary ?? fallback.scoreSummary,
    flowMetrics: payload.flowMetrics ?? [],
    flowUnavailable: payload.flowUnavailable,
    optionsShortMetrics: payload.optionsShortMetrics ?? [],
    optionsUnavailable: payload.optionsUnavailable,
    issues: payload.issueCards ?? [],
    relatedSymbols: payload.relatedSymbols ?? fallback.relatedSymbols,
  } satisfies StockFixture;
}
