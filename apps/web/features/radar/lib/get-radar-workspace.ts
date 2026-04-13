import "server-only";

import { radarFixture } from "@/dev/fixtures";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  assertResearchApiConfigured,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type {
  RadarApiResponse,
  RadarFixture,
  Tone,
  WatchlistFolderNode,
} from "@/lib/research/types";

export async function getRadarWorkspace() {
  const result = await fetchResearchApiJson<RadarApiResponse>({
    explicitUrlEnv: "RADAR_API_URL",
    basePath: "/radar",
  });

  if (result.status === "disabled") {
    assertResearchApiConfigured(result, "radar");
    return {
      ...radarFixture,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 기본 watchlist를 표시합니다.",
      }),
    };
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "radar");
    return {
      ...radarFixture,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `radar API 연결이 실패해 대체 watchlist를 표시합니다. ${result.errorMessage}`,
      }),
    };
  }

  const payload = result.payload;

  if (!payload.watchlistRows?.length) {
    return {
      ...radarFixture,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "radar API 응답에 watchlistRows가 없어 기본 watchlist를 표시합니다.",
      }),
    };
  }

  return {
    folders: mapFolders(payload.folderTree),
    rows: payload.watchlistRows.map((row) => ({
      symbol: row.symbol,
      name: row.name,
      securityCode: row.securityCode,
      sector: row.sector,
      folderId: row.folderId,
      tags: row.tags,
      price: row.price,
      changePercent: row.changePercent,
      volumeRatio: row.volumeRatio,
      relativeStrength: row.relativeStrength,
      score: row.score,
      nextEvent: row.nextEvent,
      thesis: row.thesis,
      condition: row.condition,
    })),
    sectorCards: payload.sectorCards,
    schedules: payload.keySchedule,
    issues:
      payload.keyIssues.map((item, index) => ({
        id: `radar-api-issue-${index + 1}`,
        source: "api",
        headline: item.headline,
        summary: item.summary,
        publishedAt: "",
        impactLabel: item.impact,
        tone: getToneFromImpact(item.impact),
        sector: item.sector,
      })),
    reports: payload.brokerReports,
    topPicks: payload.topPicks,
    defaultVisibleColumns: radarFixture.defaultVisibleColumns,
    defaultViewMode: radarFixture.defaultViewMode,
    defaultGroupMode: radarFixture.defaultGroupMode,
    defaultSelectedFolderId: radarFixture.defaultSelectedFolderId,
    savedViews: radarFixture.savedViews,
    dataSource: buildPayloadDataSource(payload.sourceRefs),
  } satisfies RadarFixture;
}

function mapFolders(folderTree: WatchlistFolderNode[] | undefined) {
  if (!folderTree?.length) {
    return radarFixture.folders;
  }

  return folderTree.map((folder) => mapFolderNode(folder));
}

function mapFolderNode(folder: WatchlistFolderNode): WatchlistFolderNode {
  return {
    id: folder.id,
    label: folder.label,
    count: folder.count,
    description: folder.description,
    tags: folder.tags,
    children: folder.children?.map((child) => mapFolderNode(child)),
  };
}

function getToneFromImpact(impact: string): Tone {
  const normalizedImpact = impact.trim().toLowerCase();

  if (
    normalizedImpact.includes("긍정") ||
    normalizedImpact.includes("강세") ||
    normalizedImpact.includes("우선")
  ) {
    return "positive";
  }

  if (
    normalizedImpact.includes("부정") ||
    normalizedImpact.includes("리스크") ||
    normalizedImpact.includes("경계")
  ) {
    return "negative";
  }

  return "neutral";
}
