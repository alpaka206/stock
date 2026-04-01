import "server-only";

import { findInstrument, radarFixture } from "@/dev/fixtures";
import { fetchResearchApiJson } from "@/lib/server/research-api";
import type { RadarFixture, Tone, WatchlistFolderNode } from "@/lib/research/types";

type RadarApiRow = {
  symbol: string;
  name?: string;
  securityCode?: string;
  sector: string;
  folderId?: string;
  tags?: string[];
  price: number;
  changePercent: number;
  volumeRatio: number;
  relativeStrength: number;
  score: number;
  nextEvent?: string;
  thesis: string;
  condition: string;
};

type RadarApiSectorCard = {
  sector: string;
  score: number;
  thesis: string;
  catalyst: string;
  topPick: string;
};

type RadarApiFolderNode = {
  id: string;
  label: string;
  count: number;
  description: string;
  tags?: string[];
  children?: RadarApiFolderNode[];
};

type RadarApiSourcedText = {
  text: string;
  sourceRefIds: string[];
};

type RadarApiResponse = {
  folderTree?: RadarApiFolderNode[];
  watchlistRows?: RadarApiRow[];
  sectorCards?: RadarApiSectorCard[];
  brokerReports?: RadarFixture["reports"];
  keySchedule?: RadarFixture["schedules"];
  keyIssues?: Array<{
    headline: string;
    summary: string;
    impact: string;
    sector?: string;
    sourceRefIds: string[];
  }>;
  topPicks?: RadarFixture["topPicks"];
  selectedSectorSummary?: RadarApiSourcedText;
  reportSummary?: RadarApiSourcedText[];
};

export async function getRadarWorkspace() {
  const payload = await fetchResearchApiJson<RadarApiResponse>({
    explicitUrlEnv: "RADAR_API_URL",
    basePath: "/radar",
  });

  if (!payload?.watchlistRows?.length) {
    return radarFixture;
  }

  return {
    folders: mapFolders(payload.folderTree),
    rows: payload.watchlistRows.map((row) => {
      const fallbackInstrument = findInstrument(row.symbol);

      return {
        symbol: row.symbol,
        name: row.name ?? fallbackInstrument?.name ?? row.symbol,
        securityCode:
          row.securityCode ??
          fallbackInstrument?.securityCode ??
          `${row.symbol.toUpperCase()}-000`,
        sector: row.sector,
        folderId: row.folderId ?? "all",
        tags: row.tags ?? [],
        price: row.price,
        changePercent: row.changePercent,
        volumeRatio: row.volumeRatio,
        relativeStrength: row.relativeStrength,
        score: row.score,
        nextEvent: row.nextEvent ?? "체크 필요",
        thesis: row.thesis,
        condition: row.condition,
      };
    }),
    sectorCards: payload.sectorCards ?? [],
    schedules: payload.keySchedule ?? [],
    issues:
      payload.keyIssues?.map((item, index) => ({
        id: `radar-api-issue-${index + 1}`,
        source: "api",
        headline: item.headline,
        summary: item.summary,
        publishedAt: "",
        impactLabel: item.impact,
        tone: getToneFromImpact(item.impact),
        sector: item.sector,
      })) ?? [],
    reports: payload.brokerReports ?? [],
    topPicks: payload.topPicks ?? [],
    defaultVisibleColumns: radarFixture.defaultVisibleColumns,
    defaultViewMode: radarFixture.defaultViewMode,
    defaultGroupMode: radarFixture.defaultGroupMode,
    defaultSelectedFolderId: radarFixture.defaultSelectedFolderId,
    savedViews: radarFixture.savedViews,
  } satisfies RadarFixture;
}

function mapFolders(folderTree: RadarApiFolderNode[] | undefined) {
  if (!folderTree?.length) {
    return radarFixture.folders;
  }

  return folderTree.map((folder) => mapFolderNode(folder));
}

function mapFolderNode(folder: RadarApiFolderNode): WatchlistFolderNode {
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
