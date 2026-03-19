import "server-only";

import { overviewFixture } from "@/dev/fixtures/overview";
import type {
  HeatmapTile,
  IndexStripItem,
  NewsItem,
  OverviewDriverItem,
  OverviewFixture,
  RiskBannerItem,
  SectorStrengthItem,
  Tone,
  TrendDirection,
} from "@/lib/research/types";

const DEFAULT_OVERVIEW_API_TIMEOUT_MS = 15000;

type OverviewApiSourcedText = {
  text: string;
  sourceRefIds: string[];
};

type OverviewApiBenchmarkSnapshotItem = {
  label: string;
  symbol: string;
  category: string;
  value: number;
  changePercent: number;
  note: string;
  sourceRefIds: string[];
};

type OverviewApiResponse = {
  asOf: string;
  sourceRefs: Array<{
    id: string;
    title: string;
    kind: string;
    publisher: string;
    publishedAt: string;
    url?: string;
    symbol?: string;
  }>;
  missingData: Array<{
    field: string;
    reason: string;
    expectedSource?: string;
  }>;
  confidence: {
    score: number;
    label: "low" | "medium" | "high";
    rationale: string;
  };
  benchmarkSnapshot?: OverviewApiBenchmarkSnapshotItem[];
  marketSummary: OverviewApiSourcedText;
  drivers: OverviewApiSourcedText[];
  risks: OverviewApiSourcedText[];
  sectorStrength: Array<{
    sector: string;
    score: number;
    summary: string;
    sourceRefIds: string[];
  }>;
  notableNews: Array<{
    headline: string;
    source: string;
    impact: string;
    publishedAt: string;
    url: string;
    sourceRefIds: string[];
  }>;
};

const sectorSymbolMap = [
  { keywords: ["반도체", "semiconductor"], symbol: "NVDA" },
  { keywords: ["전력", "power", "utility"], symbol: "VRT" },
  { keywords: ["보안", "security", "cyber"], symbol: "CRWD" },
  { keywords: ["클라우드", "software", "소프트웨어"], symbol: "MSFT" },
  { keywords: ["서버", "infra", "infrastructure"], symbol: "SMCI" },
] as const;

const positiveImpactKeywords = ["긍정", "우선 검토", "관심", "positive"];
const negativeImpactKeywords = ["부정", "리스크 확대", "경계", "negative"];

const heatmapFallbackBySector = new Map(
  overviewFixture.heatmap.map((tile) => [tile.label, tile])
);

export async function getOverviewSnapshot() {
  const apiUrl = resolveOverviewApiUrl();

  if (!apiUrl) {
    return overviewFixture;
  }

  try {
    const response = await fetch(apiUrl, buildOverviewRequestInit());

    if (!response.ok) {
      return overviewFixture;
    }

    const payload = (await response.json()) as OverviewApiResponse;

    return buildOverviewSnapshot(payload);
  } catch {
    return overviewFixture;
  }
}

function buildOverviewRequestInit(): RequestInit {
  const timeoutMs = getOverviewApiTimeoutMs();
  const requestInit: RequestInit = {
    headers: {
      Accept: "application/json",
    },
    next: {
      revalidate: 300,
    },
  };

  if (timeoutMs > 0 && typeof AbortSignal.timeout === "function") {
    requestInit.signal = AbortSignal.timeout(timeoutMs);
  }

  return requestInit;
}

function getOverviewApiTimeoutMs() {
  const rawValue = process.env.OVERVIEW_API_TIMEOUT_MS?.trim();

  if (!rawValue) {
    return DEFAULT_OVERVIEW_API_TIMEOUT_MS;
  }

  const parsedValue = Number(rawValue);

  if (!Number.isFinite(parsedValue) || parsedValue < 0) {
    return DEFAULT_OVERVIEW_API_TIMEOUT_MS;
  }

  return parsedValue;
}

function resolveOverviewApiUrl() {
  const explicitUrl = process.env.OVERVIEW_API_URL?.trim();

  if (explicitUrl) {
    return explicitUrl;
  }

  const baseUrl =
    process.env.STOCK_API_BASE_URL?.trim() ??
    process.env.NEXT_PUBLIC_STOCK_API_BASE_URL?.trim();

  if (!baseUrl) {
    return null;
  }

  return `${baseUrl.replace(/\/$/, "")}/overview`;
}

function buildOverviewSnapshot(payload: OverviewApiResponse): OverviewFixture {
  const driverTexts = payload.drivers.map((driver) => driver.text);
  const riskTexts = payload.risks.map((risk) => risk.text);

  return {
    asOf: formatAsOf(payload.asOf),
    lead: payload.marketSummary.text,
    scenario:
      driverTexts[0] && riskTexts[0]
        ? `${driverTexts[0]} 다만 ${riskTexts[0]}`
        : driverTexts[0] ?? riskTexts[0] ?? overviewFixture.scenario,
    summaryDrivers: buildSummaryDrivers(payload),
    indices: buildIndexItems(payload),
    news: buildNewsItems(payload),
    sectors: buildSectorItems(payload),
    risks: buildRiskItems(payload),
    heatmap: buildHeatmap(payload),
    confidence: payload.confidence,
    sourceSummary: {
      sourceCount: payload.sourceRefs.length,
      missingDataCount: payload.missingData.length,
    },
  };
}

function buildSummaryDrivers(payload: OverviewApiResponse): OverviewDriverItem[] {
  const items: OverviewDriverItem[] = [];

  payload.drivers.slice(0, 2).forEach((driver, index) => {
    items.push({
      label: index === 0 ? "주도 신호" : "추가 확인",
      text: driver.text,
      tone: index === 0 ? "positive" : "neutral",
      href: index === 0 ? "/radar" : "/history",
    });
  });

  if (payload.risks[0]) {
    items.push({
      label: "리스크",
      text: payload.risks[0].text,
      tone: "negative",
      href: "/history",
    });
  }

  if (items.length < 3 && payload.missingData.length > 0) {
    items.push({
      label: "데이터 공백",
      text: payload.missingData[0].reason,
      tone: "neutral",
      href: "/history",
    });
  }

  return items.length === 0 ? overviewFixture.summaryDrivers : items.slice(0, 3);
}

function buildIndexItems(payload: OverviewApiResponse): IndexStripItem[] {
  const benchmarkSnapshot = payload.benchmarkSnapshot ?? [];

  if (benchmarkSnapshot.length > 0) {
    return benchmarkSnapshot.map((item) => ({
      name: item.label,
      symbol: item.symbol,
      category: item.category,
      value: item.value,
      changePercent: item.changePercent,
      note: item.note,
      href: getIndexHref(item),
    }));
  }

  if (isMockPayload(payload)) {
    return overviewFixture.indices;
  }

  return [];
}

function buildNewsItems(payload: OverviewApiResponse): NewsItem[] {
  if (payload.notableNews.length === 0) {
    return overviewFixture.news;
  }

  return payload.notableNews.slice(0, 4).map((item, index) => ({
    id: `overview-api-news-${index + 1}`,
    source: item.source,
    headline: item.headline,
    summary: buildNewsSummary(item.impact),
    publishedAt: formatTime(item.publishedAt),
    impactLabel: item.impact,
    tone: getToneFromImpact(item.impact),
    href: getHrefFromImpact(item.impact),
  }));
}

function buildSectorItems(payload: OverviewApiResponse): SectorStrengthItem[] {
  if (payload.sectorStrength.length === 0) {
    return overviewFixture.sectors;
  }

  return payload.sectorStrength.slice(0, 4).map((sector) => {
    const targetSymbol = getSymbolForSector(sector.sector);

    return {
      id: sector.sector.toLowerCase().replace(/\s+/g, "-"),
      name: sector.sector,
      score: Math.round(sector.score),
      changePercent: getHeatmapChange(sector.sector),
      direction: getDirectionFromScore(sector.score),
      momentum: sector.summary,
      catalysts: buildSectorCatalysts(sector.summary),
      targetSymbol,
      href: `/stocks/${targetSymbol}`,
    };
  });
}

function buildRiskItems(payload: OverviewApiResponse): RiskBannerItem[] {
  const apiRisks = payload.risks.slice(0, 3).map((risk) => ({
    label: "체크 필요",
    value: "확인",
    detail: risk.text,
    tone: "negative" as Tone,
    href: "/history",
  }));

  if (payload.missingData.length > 0) {
    apiRisks.push({
      label: "데이터 공백",
      value: `${payload.missingData.length}건`,
      detail: payload.missingData[0].reason,
      tone: "neutral",
      href: "/history",
    });
  }

  return apiRisks.length === 0 ? overviewFixture.risks : apiRisks.slice(0, 3);
}

function buildHeatmap(payload: OverviewApiResponse): HeatmapTile[] {
  if (payload.sectorStrength.length === 0) {
    return overviewFixture.heatmap;
  }

  return payload.sectorStrength.slice(0, 6).map((sector) => {
    const fallbackTile = heatmapFallbackBySector.get(sector.sector);
    const score = Math.round(sector.score);

    return {
      label: sector.sector,
      score,
      changePercent: fallbackTile?.changePercent ?? getChangePercentFromScore(score),
      href: `/stocks/${getSymbolForSector(sector.sector)}`,
    };
  });
}

function isMockPayload(payload: OverviewApiResponse) {
  return (
    payload.sourceRefs.length > 0 &&
    payload.sourceRefs.every((sourceRef) => sourceRef.kind === "mock")
  );
}

function getSymbolForSector(sectorName: string) {
  const normalizedName = sectorName.toLowerCase();
  const matched = sectorSymbolMap.find((candidate) =>
    candidate.keywords.some((keyword) => normalizedName.includes(keyword))
  );

  return matched?.symbol ?? "NVDA";
}

function getIndexHref(item: OverviewApiBenchmarkSnapshotItem) {
  if (item.symbol === "SMH") {
    return "/stocks/NVDA";
  }

  if (item.symbol === "QQQ") {
    return "/radar";
  }

  return "/history";
}

function getDirectionFromScore(score: number): TrendDirection {
  if (score >= 72) {
    return "up";
  }

  if (score <= 48) {
    return "down";
  }

  return "flat";
}

function getChangePercentFromScore(score: number) {
  if (score >= 80) {
    return 1.5;
  }

  if (score <= 45) {
    return -0.8;
  }

  return 0.3;
}

function getHeatmapChange(sectorName: string) {
  return heatmapFallbackBySector.get(sectorName)?.changePercent ?? 0.4;
}

function buildSectorCatalysts(summary: string) {
  const segments = summary
    .split(/[,.]/)
    .map((segment) => segment.trim())
    .filter(Boolean);

  return segments.length >= 2 ? segments.slice(0, 2) : [summary];
}

function buildNewsSummary(impact: string) {
  const tone = getToneFromImpact(impact);

  if (tone === "positive") {
    return "상단 주도 섹터로 자금이 붙는지 레이더에서 바로 확인할 필요가 있습니다.";
  }

  if (tone === "negative") {
    return "과거 유사 구간의 반응을 히스토리에서 함께 비교해야 하는 headline입니다.";
  }

  return "방향성 확정보다 섹터별 상대 강도 비교가 우선인 뉴스 흐름입니다.";
}

function getToneFromImpact(impact: string): Tone {
  if (matchesImpactKeyword(impact, positiveImpactKeywords)) {
    return "positive";
  }

  if (matchesImpactKeyword(impact, negativeImpactKeywords)) {
    return "negative";
  }

  return "neutral";
}

function getHrefFromImpact(impact: string) {
  const tone = getToneFromImpact(impact);

  if (tone === "positive") {
    return "/radar";
  }

  return "/history";
}

function matchesImpactKeyword(impact: string, keywords: string[]) {
  const normalizedImpact = impact.trim().toLowerCase();
  return keywords.some((keyword) => normalizedImpact.includes(keyword.toLowerCase()));
}

function formatAsOf(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return overviewFixture.asOf;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}
