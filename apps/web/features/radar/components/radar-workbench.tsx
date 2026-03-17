"use client";

import * as React from "react";
import type { ColDef } from "ag-grid-community";
import Link from "next/link";

import { ResearchPanel } from "@/components/research/research-panel";
import { TrendChip } from "@/components/research/trend-chip";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FilterChipGroup } from "@/features/filters/components/filter-chip-group";
import { AgGridTable } from "@/features/grid/components/ag-grid-table";
import {
  GridColumnVisibilityMenu,
  type GridColumnOption,
} from "@/features/grid/components/grid-column-visibility-menu";
import { SectorSummaryPanel } from "@/features/sector/components/sector-summary-panel";
import { WatchlistFolderTree } from "@/features/watchlist/components/watchlist-folder-tree";
import { formatPrice, formatSignedPercent } from "@/lib/format";
import type {
  RadarColumnKey,
  RadarFixture,
  WatchlistFolderNode,
  WatchlistRow,
} from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type RadarWorkbenchProps = {
  workspace: RadarFixture;
};

const radarModes = [
  { value: "core", label: "핵심 보기" },
  { value: "volume", label: "거래량 보기" },
  { value: "risk", label: "리스크 보기" },
] as const;

const columnLabelMap: Record<RadarColumnKey, string> = {
  symbol: "심볼",
  name: "종목명",
  price: "가격",
  changePercent: "등락률",
  score: "점수",
  volumeRatio: "거래량 배수",
  relativeStrength: "상대강도",
  sector: "섹터",
  nextEvent: "다음 이벤트",
  thesis: "한 줄 논리",
};

export function RadarWorkbench({ workspace }: RadarWorkbenchProps) {
  const [activeFolder, setActiveFolder] = React.useState("all");
  const [viewMode, setViewMode] =
    React.useState<(typeof radarModes)[number]["value"]>("core");
  const [query, setQuery] = React.useState("");
  const [visibleColumns, setVisibleColumns] = React.useState<RadarColumnKey[]>(
    workspace.defaultVisibleColumns
  );
  const [selectedSymbol, setSelectedSymbol] = React.useState(
    workspace.rows[0]?.symbol ?? ""
  );

  const activeFolderIds = resolveActiveFolderIds(workspace.folders, activeFolder);
  const filteredRows = sortRows(
    workspace.rows.filter((row) => {
      const matchesFolder =
        activeFolderIds === null ? true : activeFolderIds.has(row.folderId);
      const matchesQuery =
        query.trim().length === 0 ||
        [row.symbol, row.name, row.sector, row.thesis]
          .join(" ")
          .toLowerCase()
          .includes(query.toLowerCase());

      return matchesFolder && matchesQuery;
    }),
    viewMode
  );

  React.useEffect(() => {
    if (!filteredRows.some((row) => row.symbol === selectedSymbol)) {
      setSelectedSymbol(filteredRows[0]?.symbol ?? workspace.rows[0]?.symbol ?? "");
    }
  }, [filteredRows, selectedSymbol, workspace.rows]);

  const selectedRow =
    filteredRows.find((row) => row.symbol === selectedSymbol) ??
    filteredRows[0] ??
    workspace.rows[0];

  const columnDefs: ColDef<WatchlistRow>[] = [
    {
      field: "symbol",
      headerName: "심볼",
      hide: !visibleColumns.includes("symbol"),
      maxWidth: 110,
      cellClass: "numeric font-semibold",
    },
    {
      field: "name",
      headerName: "종목명",
      hide: !visibleColumns.includes("name"),
      minWidth: 150,
    },
    {
      field: "price",
      headerName: "가격",
      hide: !visibleColumns.includes("price"),
      cellClass: "numeric",
      valueFormatter: ({ value }) => formatPrice(value),
    },
    {
      field: "changePercent",
      headerName: "등락률",
      hide: !visibleColumns.includes("changePercent"),
      cellRenderer: ({ value }: { value: number }) => (
        <span
          className={cn(
            "numeric font-semibold",
            value > 0 ? "tone-positive" : value < 0 ? "tone-negative" : "tone-neutral"
          )}
        >
          {formatSignedPercent(value)}
        </span>
      ),
    },
    {
      field: "score",
      headerName: "점수",
      hide: !visibleColumns.includes("score"),
      maxWidth: 92,
      cellClass: "numeric font-semibold",
    },
    {
      field: "volumeRatio",
      headerName: "거래량 배수",
      hide: !visibleColumns.includes("volumeRatio"),
      cellClass: "numeric",
      valueFormatter: ({ value }) => `${value.toFixed(2)}x`,
    },
    {
      field: "relativeStrength",
      headerName: "상대강도",
      hide: !visibleColumns.includes("relativeStrength"),
      maxWidth: 110,
      cellClass: "numeric",
    },
    {
      field: "sector",
      headerName: "섹터",
      hide: !visibleColumns.includes("sector"),
      minWidth: 120,
    },
    {
      field: "nextEvent",
      headerName: "다음 이벤트",
      hide: !visibleColumns.includes("nextEvent"),
      minWidth: 150,
    },
    {
      field: "thesis",
      headerName: "한 줄 논리",
      hide: !visibleColumns.includes("thesis"),
      flex: 1.2,
      minWidth: 220,
      tooltipField: "thesis",
    },
  ];

  const columnOptions: GridColumnOption[] = Object.entries(columnLabelMap).map(
    ([key, label]) => ({
      key,
      label,
      checked: visibleColumns.includes(key as RadarColumnKey),
      disabled: key === "symbol",
    })
  );

  return (
    <div className={layoutTokens.page}>
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className={typographyTokens.eyebrow}>Radar Workspace</p>
          <h2 className={typographyTokens.title}>
            관심종목과 섹터 인텔리전스를 같은 화면에서 검토
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            좌측 폴더, 중앙 AG Grid, 우측 요약 패널 구조로 스캐폴드했다.
            Enterprise 기능 대신 폴더 트리와 커스텀 컬럼 토글로 뷰를 구성한다.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="심볼, 섹터, 논리 검색"
            className="w-full min-w-[220px] bg-background/70 xl:w-[280px]"
          />
          <GridColumnVisibilityMenu
            options={columnOptions}
            onCheckedChange={(key, checked) => {
              const columnKey = key as RadarColumnKey;

              if (columnKey === "symbol") {
                return;
              }

              setVisibleColumns((currentColumns) => {
                if (checked) {
                  return [...currentColumns, columnKey];
                }

                return currentColumns.filter((current) => current !== columnKey);
              });
            }}
          />
        </div>
      </div>

      <div className={layoutTokens.threePanelGrid}>
        <ResearchPanel
          title="워치리스트 폴더"
          description="폴더, 태그, 전략 묶음을 트리로 정리"
        >
          <div className="space-y-4">
            <FilterChipGroup
              options={radarModes}
              value={viewMode}
              onValueChange={setViewMode}
            />
            <WatchlistFolderTree
              folders={workspace.folders}
              activeId={activeFolder}
              onSelect={setActiveFolder}
            />
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="관심종목 Grid"
          description={`${filteredRows.length}개 종목 · AG Grid Community`}
        >
          <AgGridTable
            rowData={filteredRows}
            columnDefs={columnDefs}
            emptyMessage="조건에 맞는 종목이 없습니다."
            onRowClicked={(event) => {
              if (event.data) {
                setSelectedSymbol(event.data.symbol);
              }
            }}
            gridOptions={{
              suppressMovableColumns: true,
            }}
          />
        </ResearchPanel>

        <div className="space-y-[var(--space-grid)]">
          {selectedRow ? (
            <ResearchPanel
              title={`${selectedRow.symbol} 포커스`}
              description={selectedRow.name}
              action={
                <TrendChip
                  direction={
                    selectedRow.changePercent > 0
                      ? "up"
                      : selectedRow.changePercent < 0
                        ? "down"
                        : "flat"
                  }
                  value={selectedRow.changePercent}
                />
              }
            >
              <div className="space-y-4">
                <div className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className={typographyTokens.eyebrow}>{selectedRow.sector}</p>
                      <p className="text-lg font-semibold tracking-tight">
                        {selectedRow.condition}
                      </p>
                    </div>
                    <p className="numeric text-2xl font-semibold">
                      {selectedRow.score}
                    </p>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted-foreground">
                    {selectedRow.thesis}
                  </p>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <Metric label="가격" value={formatPrice(selectedRow.price)} />
                    <Metric
                      label="거래량 배수"
                      value={`${selectedRow.volumeRatio.toFixed(2)}x`}
                    />
                    <Metric
                      label="상대강도"
                      value={selectedRow.relativeStrength.toString()}
                    />
                    <Metric label="다음 이벤트" value={selectedRow.nextEvent} />
                  </div>
                </div>
                <Button asChild className="w-full">
                  <Link href={`/stocks/${selectedRow.symbol}`}>
                    종목 분석 페이지로 이동
                  </Link>
                </Button>
              </div>
            </ResearchPanel>
          ) : null}

          <SectorSummaryPanel
            title="섹터 요약"
            description="선택 후보와 연결된 섹터 컨텍스트"
            items={workspace.sectorCards.map((item) => ({
              label: item.sector,
              score: item.score,
              summary: item.thesis,
              meta: `${item.catalyst} · Top Pick ${item.topPick}`,
            }))}
          />

          <ResearchPanel title="브로커 메모" description="오늘 읽을 리포트 요점">
            <div className="space-y-3">
              {workspace.reports.map((report) => (
                <div
                  key={`${report.house}-${report.symbol}`}
                  className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold tracking-tight">
                      {report.house} · {report.symbol}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {report.stance}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {report.summary}
                  </p>
                </div>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="섹터 일정" description="장중 체크 포인트">
            <div className="space-y-3">
              {workspace.schedules.map((schedule) => (
                <div
                  key={`${schedule.time}-${schedule.title}`}
                  className="flex items-start justify-between gap-3 rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
                >
                  <div>
                    <p className="text-sm font-semibold tracking-tight">
                      {schedule.title}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {schedule.note}
                    </p>
                  </div>
                  <span className="numeric text-xs font-semibold text-muted-foreground">
                    {schedule.time}
                  </span>
                </div>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="섹터 이슈" description="오른쪽 패널 피드 샘플">
            <div className="space-y-3">
              {workspace.issues.map((issue) => (
                <div
                  key={issue.id}
                  className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
                >
                  <p className="text-sm font-semibold tracking-tight">
                    {issue.headline}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {issue.summary}
                  </p>
                </div>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="Top Pick" description="섹터별 우선검토 후보">
            <div className="space-y-3">
              {workspace.topPicks.map((topPick) => (
                <Link
                  key={topPick.symbol}
                  href={`/stocks/${topPick.symbol}`}
                  className="flex items-center justify-between gap-3 rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3 transition-colors hover:bg-muted/60"
                >
                  <div>
                    <p className="text-sm font-semibold tracking-tight">
                      {topPick.symbol}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {topPick.reason}
                    </p>
                  </div>
                  <span className="numeric text-lg font-semibold">
                    {topPick.score}
                  </span>
                </Link>
              ))}
            </div>
          </ResearchPanel>
        </div>
      </div>
    </div>
  );
}

function sortRows(rows: WatchlistRow[], viewMode: (typeof radarModes)[number]["value"]) {
  const copiedRows = [...rows];

  if (viewMode === "volume") {
    copiedRows.sort((left, right) => right.volumeRatio - left.volumeRatio);
    return copiedRows;
  }

  if (viewMode === "risk") {
    const riskOrder = {
      "리스크 확대": 0,
      "조건부 강세": 1,
      관심: 2,
      우선검토: 3,
    } as const;

    copiedRows.sort((left, right) => {
      const byCondition =
        riskOrder[left.condition as keyof typeof riskOrder] -
        riskOrder[right.condition as keyof typeof riskOrder];

      if (byCondition !== 0) {
        return byCondition;
      }

      return Math.abs(right.changePercent) - Math.abs(left.changePercent);
    });

    return copiedRows;
  }

  copiedRows.sort((left, right) => right.score - left.score);
  return copiedRows;
}

function resolveActiveFolderIds(
  folders: WatchlistFolderNode[],
  activeFolderId: string
) {
  if (activeFolderId === "all") {
    return null;
  }

  const targetNode = findFolderNode(folders, activeFolderId);

  if (!targetNode) {
    return null;
  }

  return new Set(collectFolderIds(targetNode));
}

function findFolderNode(
  folders: WatchlistFolderNode[],
  targetId: string
): WatchlistFolderNode | null {
  for (const folder of folders) {
    if (folder.id === targetId) {
      return folder;
    }

    if (folder.children) {
      const foundFolder = findFolderNode(folder.children, targetId);

      if (foundFolder) {
        return foundFolder;
      }
    }
  }

  return null;
}

function collectFolderIds(folder: WatchlistFolderNode): string[] {
  return [
    folder.id,
    ...(folder.children?.flatMap((childFolder) => collectFolderIds(childFolder)) ??
      []),
  ];
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border/50 bg-background/40 px-3 py-2">
      <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </p>
      <p className="numeric mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}
