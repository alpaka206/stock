"use client";

import * as React from "react";
import type { ColDef } from "ag-grid-community";
import Link from "next/link";

import { ResearchPanel } from "@/components/research/research-panel";
import { TrendChip } from "@/components/research/trend-chip";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FilterChipGroup } from "@/features/filters/components/filter-chip-group";
import { AgGridTable } from "@/features/grid/components/ag-grid-table";
import {
  GridColumnVisibilityMenu,
  type GridColumnOption,
} from "@/features/grid/components/grid-column-visibility-menu";
import { SectorSummaryPanel } from "@/features/sector/components/sector-summary-panel";
import { WatchlistFolderTree } from "@/features/watchlist/components/watchlist-folder-tree";
import { formatPrice, formatSignedPercent } from "@/lib/format";
import { useStoredPresets } from "@/lib/client/use-stored-presets";
import { useDebouncedValue, useUrlState } from "@/lib/client/use-url-state";
import type {
  RadarColumnKey,
  RadarFixture,
  RadarGroupMode,
  RadarSortItem,
  RadarViewMode,
  SavedViewPreset,
  ScheduleItem,
  WatchlistFolderNode,
  WatchlistRow,
} from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type RadarWorkbenchProps = {
  workspace: RadarFixture;
};

type SortOption = {
  value: string;
  label: string;
  sortModel: RadarSortItem[];
};

const radarModeOptions = [
  { value: "core", label: "코어 보기" },
  { value: "volume", label: "거래량 보기" },
  { value: "risk", label: "리스크 보기" },
] as const satisfies ReadonlyArray<{ value: RadarViewMode; label: string }>;

const groupModeOptions = [
  { value: "flat", label: "단일 그리드" },
  { value: "sector", label: "섹터 묶음" },
] as const satisfies ReadonlyArray<{ value: RadarGroupMode; label: string }>;

const sortOptions: SortOption[] = [
  {
    value: "score-desc",
    label: "점수 높은 순",
    sortModel: [{ colId: "score", sort: "desc" }],
  },
  {
    value: "change-desc",
    label: "상승률 높은 순",
    sortModel: [{ colId: "changePercent", sort: "desc" }],
  },
  {
    value: "volume-desc",
    label: "거래량 배수 높은 순",
    sortModel: [{ colId: "volumeRatio", sort: "desc" }],
  },
  {
    value: "sector-asc",
    label: "섹터 순",
    sortModel: [
      { colId: "sector", sort: "asc" },
      { colId: "score", sort: "desc" },
    ],
  },
];

const columnLabelMap: Record<RadarColumnKey, string> = {
  symbol: "티커",
  name: "종목명",
  securityCode: "종목번호",
  price: "가격",
  changePercent: "등락률",
  score: "점수",
  volumeRatio: "거래량 배수",
  relativeStrength: "상대강도",
  sector: "섹터",
  nextEvent: "다음 이벤트",
  thesis: "핵심 논리",
};

export function RadarWorkbench({ workspace }: RadarWorkbenchProps) {
  const { searchParams, replaceParams } = useUrlState();
  const [draftQuery, setDraftQuery] = React.useState(searchParams.get("q") ?? "");
  const [presetName, setPresetName] = React.useState("");
  const debouncedQuery = useDebouncedValue(draftQuery, 160);

  const { presets, savePreset, removePreset } = useStoredPresets(
    "stock-workspace:radar-presets",
    workspace.savedViews
  );

  React.useEffect(() => {
    setDraftQuery(searchParams.get("q") ?? "");
  }, [searchParams]);

  React.useEffect(() => {
    replaceParams({ q: debouncedQuery || undefined });
  }, [debouncedQuery, replaceParams]);

  const folderId =
    searchParams.get("folder") ?? workspace.defaultSelectedFolderId ?? "all";
  const viewMode = parseViewMode(
    searchParams.get("view"),
    workspace.defaultViewMode
  );
  const groupMode = parseGroupMode(
    searchParams.get("group"),
    workspace.defaultGroupMode
  );
  const sortValue = searchParams.get("sort") ?? sortOptions[0].value;
  const selectedSymbolParam = searchParams.get("symbol") ?? "";
  const selectedSectorParam = searchParams.get("sector") ?? "";
  const visibleColumns = parseVisibleColumns(
    searchParams.get("cols"),
    workspace.defaultVisibleColumns
  );
  const activeFolderIds = resolveActiveFolderIds(workspace.folders, folderId);

  const allTags = Array.from(
    new Set(workspace.rows.flatMap((row) => row.tags.map((tag) => tag.trim())))
  ).sort((left, right) => left.localeCompare(right, "ko-KR"));

  const sortModel =
    sortOptions.find((option) => option.value === sortValue)?.sortModel ??
    sortOptions[0].sortModel;

  const normalizedQuery = debouncedQuery.trim().toLowerCase();
  const filteredRows = sortRadarRows(
    workspace.rows.filter((row) => {
      const matchesFolder =
        activeFolderIds === null ? true : activeFolderIds.has(row.folderId);
      const matchesSector =
        selectedSectorParam.trim().length === 0
          ? true
          : row.sector === selectedSectorParam;
      const matchesQuery =
        normalizedQuery.length === 0
          ? true
          : [
              row.symbol,
              row.name,
              row.securityCode,
              row.sector,
              row.thesis,
              row.tags.join(" "),
            ]
              .join(" ")
              .toLowerCase()
              .includes(normalizedQuery);

      return matchesFolder && matchesSector && matchesQuery;
    }),
    sortModel,
    viewMode
  );

  const selectedRow =
    filteredRows.find((row) => row.symbol === selectedSymbolParam) ??
    filteredRows[0] ??
    workspace.rows[0];
  const activeSector =
    selectedSectorParam ||
    selectedRow?.sector ||
    filteredRows[0]?.sector ||
    workspace.sectorCards[0]?.sector ||
    "";
  const groupedRows = groupRowsBySector(filteredRows);
  const selectedSectorCard =
    workspace.sectorCards.find((card) => card.sector === activeSector) ??
    workspace.sectorCards[0];
  const selectedReports = filterBySector(workspace.reports, activeSector);
  const selectedSchedules = filterBySector(workspace.schedules, activeSector);
  const selectedIssues = workspace.issues.filter(
    (issue) => !issue.sector || issue.sector === activeSector
  );
  const selectedTopPicks = filterBySector(workspace.topPicks, activeSector);
  const selectedPreset = presets.find(
    (preset) => preset.id === searchParams.get("preset")
  );

  const columnDefs: ColDef<WatchlistRow>[] = React.useMemo(
    () => [
      {
        field: "symbol",
        headerName: "티커",
        hide: !visibleColumns.includes("symbol"),
        maxWidth: 110,
        cellClass: "numeric font-semibold",
      },
      {
        field: "name",
        headerName: "종목명",
        hide: !visibleColumns.includes("name"),
        minWidth: 140,
      },
      {
        field: "securityCode",
        headerName: "종목번호",
        hide: !visibleColumns.includes("securityCode"),
        minWidth: 112,
        cellClass: "numeric text-muted-foreground",
      },
      {
        field: "price",
        headerName: "가격",
        hide: !visibleColumns.includes("price"),
        cellClass: "numeric",
        valueFormatter: ({ value }) => formatPrice(value ?? 0),
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
        valueFormatter: ({ value }) => `${Number(value ?? 0).toFixed(2)}x`,
      },
      {
        field: "relativeStrength",
        headerName: "상대강도",
        hide: !visibleColumns.includes("relativeStrength"),
        cellClass: "numeric",
      },
      {
        field: "sector",
        headerName: "섹터",
        hide: !visibleColumns.includes("sector"),
        minWidth: 128,
      },
      {
        field: "nextEvent",
        headerName: "다음 이벤트",
        hide: !visibleColumns.includes("nextEvent"),
        minWidth: 150,
      },
      {
        field: "thesis",
        headerName: "핵심 논리",
        hide: !visibleColumns.includes("thesis"),
        flex: 1.3,
        minWidth: 220,
        tooltipField: "thesis",
      },
    ],
    [visibleColumns]
  );

  const columnOptions: GridColumnOption[] = Object.entries(columnLabelMap).map(
    ([key, label]) => ({
      key,
      label,
      checked: visibleColumns.includes(key as RadarColumnKey),
      disabled: key === "symbol",
    })
  );

  const currentViewState = {
    folderId,
    query: debouncedQuery,
    viewMode,
    groupMode,
    sector: selectedSectorParam,
    selectedSymbol: selectedRow?.symbol ?? "",
    visibleColumns,
    sortModel,
  };

  return (
    <div className={layoutTokens.page}>
      <div className="space-y-3">
        <p className={typographyTokens.eyebrow}>Radar Workspace</p>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <h2 className={typographyTokens.title}>
              관심종목과 섹터 분석을 같은 화면에서 정리하는 핵심 작업대
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              좌측은 폴더와 태그, 중앙은 AG Grid 기반 워치리스트, 우측은 선택
              섹터 컨텍스트다. 컬럼 가시성, 정렬, 필터, 저장된 뷰 preset을 모두
              유지하면서 다음 분석 화면으로 자연스럽게 이어진다.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              value={draftQuery}
              onChange={(event) => setDraftQuery(event.target.value)}
              placeholder="티커, 종목명, 종목번호, 태그 검색"
              className="w-full min-w-[240px] bg-background/70 xl:w-[300px]"
            />
            <GridColumnVisibilityMenu
              options={columnOptions}
              onCheckedChange={(key, checked) => {
                const columnKey = key as RadarColumnKey;

                if (columnKey === "symbol") {
                  return;
                }

                const nextColumns = checked
                  ? Array.from(new Set([...visibleColumns, columnKey]))
                  : visibleColumns.filter((item) => item !== columnKey);

                replaceParams({
                  cols: nextColumns.join(","),
                  preset: undefined,
                });
              }}
            />
          </div>
        </div>
      </div>

      <div className={layoutTokens.threePanelGrid}>
        <ResearchPanel
          title="폴더 / 태그 / preset"
          description="왼쪽 트리에서 감시 그룹과 저장된 작업 뷰를 고른다."
        >
          <div className="space-y-5">
            <FilterChipGroup
              options={groupModeOptions}
              value={groupMode}
              onValueChange={(value) =>
                replaceParams({
                  group: value,
                  preset: undefined,
                })
              }
            />
            <WatchlistFolderTree
              folders={workspace.folders}
              activeId={folderId}
              onSelect={(nextFolderId) =>
                replaceParams({
                  folder: nextFolderId,
                  symbol: undefined,
                  preset: undefined,
                })
              }
            />

            <div className="space-y-3">
              <p className={typographyTokens.eyebrow}>태그 바로가기</p>
              <div className="flex flex-wrap gap-2">
                <TagChip
                  active={selectedSectorParam.length === 0}
                  label="전체"
                  onClick={() => replaceParams({ sector: undefined, preset: undefined })}
                />
                {allTags.map((tag) => (
                  <TagChip
                    key={tag}
                    active={draftQuery.trim() === tag}
                    label={`#${tag}`}
                    onClick={() => {
                      setDraftQuery(tag);
                      replaceParams({ preset: undefined });
                    }}
                  />
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <p className={typographyTokens.eyebrow}>저장된 뷰</p>
              <div className="flex gap-2">
                <Input
                  value={presetName}
                  onChange={(event) => setPresetName(event.target.value)}
                  placeholder="preset 이름"
                  className="bg-background/70"
                />
                <Button
                  type="button"
                  size="sm"
                  onClick={() => {
                    const trimmedName = presetName.trim();

                    if (!trimmedName) {
                      return;
                    }

                    savePreset(trimmedName, currentViewState);
                    setPresetName("");
                  }}
                >
                  저장
                </Button>
              </div>
              <div className="space-y-2">
                {presets.map((preset) => (
                  <PresetRow
                    key={preset.id}
                    preset={preset}
                    active={selectedPreset?.id === preset.id}
                    onApply={() =>
                      applyPreset({
                        preset,
                        replaceParams,
                      })
                    }
                    onRemove={() => removePreset(preset.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="관심종목 Grid"
          description={`${filteredRows.length}개 종목 · AG Grid Community 기반`}
        >
          <div className="space-y-4">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <FilterChipGroup
                options={radarModeOptions}
                value={viewMode}
                onValueChange={(value) =>
                  replaceParams({
                    view: value,
                    preset: undefined,
                  })
                }
              />
              <div className="flex flex-wrap items-center gap-2">
                <Select
                  value={sortValue}
                  onValueChange={(value) =>
                    replaceParams({
                      sort: value,
                      preset: undefined,
                    })
                  }
                >
                  <SelectTrigger className="min-w-[170px] bg-background/65">
                    <SelectValue placeholder="정렬" />
                  </SelectTrigger>
                  <SelectContent>
                    {sortOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    replaceParams({
                      folder: workspace.defaultSelectedFolderId,
                      q: undefined,
                      view: workspace.defaultViewMode,
                      group: workspace.defaultGroupMode,
                      sort: sortOptions[0].value,
                      sector: undefined,
                      symbol: undefined,
                      cols: workspace.defaultVisibleColumns.join(","),
                      preset: undefined,
                    })
                  }
                >
                  뷰 초기화
                </Button>
              </div>
            </div>

            {groupMode === "flat" ? (
              <AgGridTable
                rowData={filteredRows}
                columnDefs={columnDefs}
                className="h-[560px]"
                emptyMessage="조건에 맞는 관심종목이 없습니다."
                onRowClicked={(event) => {
                  if (!event.data) {
                    return;
                  }

                  replaceParams({
                    symbol: event.data.symbol,
                    sector: event.data.sector,
                    preset: undefined,
                  });
                }}
                gridOptions={{
                  suppressMovableColumns: true,
                }}
              />
            ) : (
              <div className="space-y-4">
                {groupedRows.map(([sector, rows]) => (
                  <div key={sector} className="space-y-2">
                    <div className="flex items-center justify-between gap-3">
                      <button
                        type="button"
                        onClick={() =>
                          replaceParams({ sector, preset: undefined, symbol: rows[0]?.symbol })
                        }
                        className="text-left"
                      >
                        <p className="text-sm font-semibold tracking-tight">{sector}</p>
                        <p className="text-xs text-muted-foreground">
                          {rows.length}개 종목 · 섹터 묶음 보기
                        </p>
                      </button>
                    </div>
                    <AgGridTable
                      rowData={rows}
                      columnDefs={columnDefs}
                      className="h-[260px]"
                      emptyMessage="표시할 종목이 없습니다."
                      onRowClicked={(event) => {
                        if (!event.data) {
                          return;
                        }

                        replaceParams({
                          symbol: event.data.symbol,
                          sector: event.data.sector,
                          preset: undefined,
                        });
                      }}
                      gridOptions={{
                        suppressMovableColumns: true,
                      }}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </ResearchPanel>

        <div className="space-y-[var(--space-grid)]">
          {selectedRow ? (
            <ResearchPanel
              title={`${selectedRow.symbol} 워크스테이션`}
              description={`${selectedRow.name} · ${selectedRow.securityCode}`}
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
                    <p className="numeric text-2xl font-semibold">{selectedRow.score}</p>
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
                      value={`${selectedRow.relativeStrength}`}
                    />
                    <Metric label="다음 이벤트" value={selectedRow.nextEvent} />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Button asChild className="w-full">
                    <Link href={`/stocks/${selectedRow.symbol}`}>
                      종목 워크스테이션 열기
                    </Link>
                  </Button>
                  <Button asChild variant="outline" className="w-full">
                    <Link href={`/history?symbol=${selectedRow.symbol}`}>
                      과거 이벤트 리플레이 보기
                    </Link>
                  </Button>
                </div>
              </div>
            </ResearchPanel>
          ) : null}

          <SectorSummaryPanel
            title="선택 섹터 요약"
            description={`${activeSector || "섹터 미선택"} 기준으로 우측 컨텍스트를 갱신한다.`}
            items={workspace.sectorCards
              .filter((item) => !activeSector || item.sector === activeSector)
              .map((item) => ({
                label: item.sector,
                score: item.score,
                summary: item.thesis,
                meta: `${item.catalyst} · Top Pick ${item.topPick}`,
              }))}
          />

          {selectedSectorCard ? (
            <ResearchPanel title="섹터 컨텍스트" description={selectedSectorCard.sector}>
              <div className="space-y-3">
                <p className="text-sm leading-6 text-muted-foreground">
                  {selectedSectorCard.thesis}
                </p>
                <Metric label="촉매" value={selectedSectorCard.catalyst} />
                <Button asChild variant="outline" className="w-full">
                  <Link href={`/stocks/${selectedSectorCard.topPick}`}>
                    Top Pick {selectedSectorCard.topPick} 보기
                  </Link>
                </Button>
              </div>
            </ResearchPanel>
          ) : null}

          <ResearchPanel title="리포트 요약" description={`${activeSector} 기준 브로커 메모`}>
            <div className="space-y-3">
              {selectedReports.map((report) => (
                <div
                  key={`${report.house}-${report.symbol}`}
                  className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold tracking-tight">
                      {report.house} · {report.symbol}
                    </p>
                    <span className="text-xs text-muted-foreground">{report.stance}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {report.summary}
                  </p>
                </div>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="일정" description="선택 섹터 기준 체크할 이벤트">
            <div className="space-y-3">
              {selectedSchedules.map((schedule) => (
                <ScheduleRow key={`${schedule.time}-${schedule.title}`} schedule={schedule} />
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="주요 이슈" description="선택 섹터에 따라 우측 패널이 갱신된다.">
            <div className="space-y-3">
              {selectedIssues.map((issue) => (
                <div
                  key={issue.id}
                  className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold tracking-tight">
                      {issue.headline}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {issue.impactLabel}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {issue.summary}
                  </p>
                </div>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="Top Pick" description="현재 섹터에서 우선 검토할 종목">
            <div className="space-y-3">
              {selectedTopPicks.map((topPick) => (
                <Link
                  key={topPick.symbol}
                  href={`/stocks/${topPick.symbol}`}
                  className="flex items-center justify-between gap-3 rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3 transition-colors hover:bg-muted/60"
                >
                  <div>
                    <p className="text-sm font-semibold tracking-tight">{topPick.symbol}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{topPick.reason}</p>
                  </div>
                  <span className="numeric text-lg font-semibold">{topPick.score}</span>
                </Link>
              ))}
            </div>
          </ResearchPanel>
        </div>
      </div>
    </div>
  );
}

function parseViewMode(value: string | null, fallback: RadarViewMode): RadarViewMode {
  if (value === "volume" || value === "risk" || value === "core") {
    return value;
  }

  return fallback;
}

function parseGroupMode(
  value: string | null,
  fallback: RadarGroupMode
): RadarGroupMode {
  if (value === "flat" || value === "sector") {
    return value;
  }

  return fallback;
}

function parseVisibleColumns(
  value: string | null,
  fallback: RadarColumnKey[]
): RadarColumnKey[] {
  if (!value) {
    return fallback;
  }

  const parsed = value
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is RadarColumnKey => item in columnLabelMap);

  return parsed.length > 0 ? parsed : fallback;
}

function sortRadarRows(
  rows: WatchlistRow[],
  sortModel: RadarSortItem[],
  viewMode: RadarViewMode
) {
  const copiedRows = [...rows];

  copiedRows.sort((left, right) => {
    for (const item of sortModel) {
      const direction = item.sort === "asc" ? 1 : -1;
      const leftValue = left[item.colId];
      const rightValue = right[item.colId];

      if (leftValue === rightValue) {
        continue;
      }

      if (typeof leftValue === "number" && typeof rightValue === "number") {
        return (leftValue - rightValue) * direction;
      }

      return String(leftValue).localeCompare(String(rightValue), "ko-KR") * direction;
    }

    if (viewMode === "volume") {
      return right.volumeRatio - left.volumeRatio;
    }

    if (viewMode === "risk") {
      return Math.abs(right.changePercent) - Math.abs(left.changePercent);
    }

    return right.score - left.score;
  });

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
    ...(folder.children?.flatMap((childFolder) => collectFolderIds(childFolder)) ?? []),
  ];
}

function groupRowsBySector(rows: WatchlistRow[]) {
  const grouped = new Map<string, WatchlistRow[]>();

  rows.forEach((row) => {
    const currentRows = grouped.get(row.sector) ?? [];
    currentRows.push(row);
    grouped.set(row.sector, currentRows);
  });

  return Array.from(grouped.entries());
}

function filterBySector<TItem extends { sector?: string }>(
  items: TItem[],
  sector: string
) {
  const filtered = items.filter((item) => !item.sector || item.sector === sector);
  return filtered.length > 0 ? filtered : items;
}

function applyPreset({
  preset,
  replaceParams,
}: {
  preset: SavedViewPreset<{
    folderId: string;
    query: string;
    viewMode: RadarViewMode;
    groupMode: RadarGroupMode;
    sector: string;
    selectedSymbol: string;
    visibleColumns: RadarColumnKey[];
    sortModel: RadarSortItem[];
  }>;
  replaceParams: (updates: Record<string, string | null | undefined>) => void;
}) {
  const matchedSortOption =
    sortOptions.find((option) =>
      JSON.stringify(option.sortModel) === JSON.stringify(preset.value.sortModel)
    )?.value ?? sortOptions[0].value;

  replaceParams({
    folder: preset.value.folderId,
    q: preset.value.query,
    view: preset.value.viewMode,
    group: preset.value.groupMode,
    sector: preset.value.sector,
    symbol: preset.value.selectedSymbol,
    cols: preset.value.visibleColumns.join(","),
    sort: matchedSortOption,
    preset: preset.id,
  });
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

function TagChip({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors",
        active
          ? "border-primary/35 bg-primary/10 text-foreground"
          : "border-border/70 bg-background/45 text-muted-foreground hover:bg-muted/60"
      )}
    >
      {label}
    </button>
  );
}

function ScheduleRow({ schedule }: { schedule: ScheduleItem }) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3">
      <div>
        <p className="text-sm font-semibold tracking-tight">{schedule.title}</p>
        <p className="mt-1 text-xs text-muted-foreground">{schedule.note}</p>
      </div>
      <span className="numeric text-xs font-semibold text-muted-foreground">
        {schedule.time}
      </span>
    </div>
  );
}

function PresetRow({
  preset,
  active,
  onApply,
  onRemove,
}: {
  preset: SavedViewPreset<unknown>;
  active: boolean;
  onApply: () => void;
  onRemove: () => void;
}) {
  return (
    <div
      className={cn(
        "rounded-[calc(var(--radius)*1.05)] border p-3",
        active
          ? "border-primary/35 bg-primary/10"
          : "border-border/60 bg-background/30"
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold tracking-tight">{preset.name}</p>
          <p className="text-xs text-muted-foreground">
            {new Intl.DateTimeFormat("ko-KR", {
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
            }).format(new Date(preset.updatedAt))}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button type="button" size="sm" variant="outline" onClick={onApply}>
            적용
          </Button>
          <Button type="button" size="sm" variant="ghost" onClick={onRemove}>
            삭제
          </Button>
        </div>
      </div>
    </div>
  );
}
