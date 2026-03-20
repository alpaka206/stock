import "server-only";

import { buildHistoryFixture } from "@/dev/fixtures";
import { fetchResearchApiJson } from "@/lib/server/research-api";
import type { HistoryFixture } from "@/lib/research/types";

type HistoryReplayParams = {
  symbol?: string;
  range?: string;
  from?: string;
  to?: string;
};

type HistoryApiResponse = {
  symbol?: string;
  rangeLabel?: string;
  availableRanges?: HistoryFixture["availableRanges"];
  priceSeries?: HistoryFixture["priceSeries"];
  eventMarkers?: HistoryFixture["eventMarkers"];
  eventTimeline?: HistoryFixture["events"];
  moveSummary?: {
    text: string;
    sourceRefIds: string[];
  };
  moveReasons?: HistoryFixture["moveReasons"];
  overlappingIndicators?: HistoryFixture["overlaps"];
};

export async function getHistoryReplay(params: HistoryReplayParams = {}) {
  const fallback = buildHistoryFixture(params.symbol);
  const payload = await fetchResearchApiJson<HistoryApiResponse>({
    explicitUrlEnv: "HISTORY_API_URL",
    basePath: "/history",
    query: {
      symbol: params.symbol?.toUpperCase(),
      range: params.range,
      from: params.from,
      to: params.to,
    },
  });

  if (!payload?.priceSeries?.length || !payload.eventTimeline?.length) {
    return fallback;
  }

  return {
    symbol: payload.symbol ?? fallback.symbol,
    range: payload.rangeLabel ?? fallback.range,
    availableRanges: payload.availableRanges ?? fallback.availableRanges,
    priceSeries: payload.priceSeries,
    eventMarkers: payload.eventMarkers ?? [],
    events: payload.eventTimeline,
    moveSummary: payload.moveSummary?.text ?? fallback.moveSummary,
    moveReasons: payload.moveReasons ?? fallback.moveReasons,
    overlaps: payload.overlappingIndicators ?? fallback.overlaps,
  } satisfies HistoryFixture;
}
