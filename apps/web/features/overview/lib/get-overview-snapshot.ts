import "server-only";

import { overviewFixture } from "@/dev/fixtures/overview";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type {
  HeatmapTile,
  IndexStripItem,
  NewsItem,
  OverviewApiBenchmarkSnapshotItem,
  OverviewApiResponse,
  OverviewDriverItem,
  OverviewFixture,
  RiskBannerItem,
  SectorStrengthItem,
  Tone,
  TrendDirection,
} from "@/lib/research/types";

const DEFAULT_OVERVIEW_API_TIMEOUT_MS = 15000;

const sectorSymbolMap = [
  { keywords: ["반도체", "semiconductor"], symbol: "NVDA" },
  { keywords: ["전력", "power", "utility"], symbol: "VRT" },
  { keywords: ["보안", "security", "cyber"], symbol: "CRWD" },
  { keywords: ["클라우드", "software", "소프트웨어"], symbol: "MSFT" },
  { keywords: ["서버", "infra", "infrastructure"], symbol: "SMCI" },
] as const;

const positiveImpactKeywords = ["긍정", "우선 검토", "관심", "positive"];
const negativeImpactKeywords = ["부정", "리스크 확대", "경계", "negative"];

type SectorNavigationTarget = {
  href: string;
  targetSymbol: string;
};

export async function getOverviewSnapshot() {
  const result = await fetchResearchApiJson<OverviewApiResponse>({
    explicitUrlEnv: "OVERVIEW_API_URL",
    basePath: "/overview",
    timeoutMs: getOverviewApiTimeoutMs(),
  });

  if (result.status === "success") {
    return buildOverviewSnapshot(result.payload);
  }

  if (result.status === "disabled") {
    return {
      ...overviewFixture,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 샘플 데이터를 표시합니다.",
      }),
    };
  }

  assertResearchApiAvailable(result, "overview");

  return {
    ...overviewFixture,
    dataSource: buildFixtureDataSource({
      fallback: allowFixtureFallback(),
      reason: `overview API 연결이 실패해 샘플 데이터를 대신 표시합니다. ${result.errorMessage}`,
    }),
  };
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

function buildOverviewSnapshot(payload: OverviewApiResponse): OverviewFixture {
  const driverTexts = payload.drivers.map((driver) => driver.text);
  const riskTexts = payload.risks.map((risk) => risk.text);
  const usesBenchmarkFallback = shouldUseBenchmarkFallback(payload);

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
    dataSource: usesBenchmarkFallback
      ? buildFixtureDataSource({
          fallback: true,
          reason:
            "overview API 응답에 benchmarkSnapshot이 없어 지수 스트립은 샘플 데이터를 사용합니다.",
        })
      : buildPayloadDataSource(payload.sourceRefs),
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

  if (items.length === 0) {
    return isMockPayload(payload) ? overviewFixture.summaryDrivers : [];
  }

  return items.slice(0, 3);
}

function buildIndexItems(payload: OverviewApiResponse): IndexStripItem[] {
  if (shouldUseBenchmarkFallback(payload)) {
    return overviewFixture.indices;
  }

  const benchmarkSnapshot = Array.isArray(payload.benchmarkSnapshot)
    ? payload.benchmarkSnapshot
    : [];

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

function shouldUseBenchmarkFallback(payload: OverviewApiResponse) {
  return (
    payload.benchmarkSnapshot === undefined ||
    (Array.isArray(payload.benchmarkSnapshot) &&
      payload.benchmarkSnapshot.length === 0 &&
      !isMockPayload(payload))
  );
}

function buildNewsItems(payload: OverviewApiResponse): NewsItem[] {
  if (payload.notableNews.length === 0) {
    return isMockPayload(payload) ? overviewFixture.news : [];
  }

  return payload.notableNews.slice(0, 4).map((item, index) => ({
    id: `overview-api-news-${index + 1}`,
    source: item.source,
    headline: item.headline,
    summary: item.summary?.trim() || "",
    publishedAt: formatTime(item.publishedAt),
    impactLabel: item.impact,
    tone: getToneFromImpact(item.impact),
    href: getHrefFromImpact(item.impact),
  }));
}

function buildSectorItems(payload: OverviewApiResponse): SectorStrengthItem[] {
  if (payload.sectorStrength.length === 0) {
    return isMockPayload(payload) ? overviewFixture.sectors : [];
  }

  return payload.sectorStrength.slice(0, 4).map((sector) => {
    const navigationTarget = getSectorNavigationTarget(sector.sector);

    return {
      id: sector.sector.toLowerCase().replace(/\s+/g, "-"),
      name: sector.sector,
      score: Math.round(sector.score),
      changePercent: sector.changePercent,
      direction: getDirectionFromScore(sector.score),
      momentum: sector.summary,
      catalysts: buildSectorCatalysts(sector.summary),
      targetSymbol: navigationTarget.targetSymbol,
      href: navigationTarget.href,
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

  if (apiRisks.length === 0) {
    return isMockPayload(payload) ? overviewFixture.risks : [];
  }

  return apiRisks.slice(0, 3);
}

function buildHeatmap(payload: OverviewApiResponse): HeatmapTile[] {
  if (payload.sectorStrength.length === 0) {
    return isMockPayload(payload) ? overviewFixture.heatmap : [];
  }

  return payload.sectorStrength.slice(0, 6).map((sector) => {
    const score = Math.round(sector.score);
    const navigationTarget = getSectorNavigationTarget(sector.sector);

    return {
      label: sector.sector,
      score,
      changePercent: sector.changePercent,
      href: navigationTarget.href,
    };
  });
}

function isMockPayload(payload: OverviewApiResponse) {
  return (
    payload.sourceRefs.length > 0 &&
    payload.sourceRefs.every((sourceRef) => sourceRef.kind === "mock")
  );
}

function getSectorNavigationTarget(sectorName: string): SectorNavigationTarget {
  const normalizedName = sectorName.toLowerCase();
  const matched = sectorSymbolMap.find((candidate) =>
    candidate.keywords.some((keyword) => normalizedName.includes(keyword))
  );

  if (!matched) {
    return {
      href: "/radar",
      targetSymbol: "레이더",
    };
  }

  return {
    href: `/stocks/${matched.symbol}`,
    targetSymbol: matched.symbol,
  };
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

function buildSectorCatalysts(summary: string) {
  const segments = summary
    .split(/[,.]/)
    .map((segment) => segment.trim())
    .filter(Boolean);

  return segments.length >= 2 ? segments.slice(0, 2) : [summary];
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
