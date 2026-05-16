"use client";

import * as React from "react";
import { RotateCcw, Search, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { DataSourceNotice } from "@/components/research/data-source-notice";
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
import { SectorSummaryPanel } from "@/features/sector/components/sector-summary-panel";
import { WatchlistFolderTree } from "@/features/watchlist/components/watchlist-folder-tree";
import { useStoredPresets } from "@/lib/client/use-stored-presets";
import { useDebouncedValue, useUrlState } from "@/lib/client/use-url-state";
import { formatPrice, formatSignedPercent } from "@/lib/format";
import type {
  RadarColumnKey,
  RadarDetectedAlert,
  RadarFixture,
  RadarGroupMode,
  RadarSortItem,
  RadarViewMode,
  RadarViewPresetState,
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
  { value: "core", label: "핵심" },
  { value: "volume", label: "거래량" },
  { value: "risk", label: "변동성" },
] as const satisfies ReadonlyArray<{ value: RadarViewMode; label: string }>;

const groupModeOptions = [
  { value: "flat", label: "전체" },
  { value: "sector", label: "섹터별" },
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
    label: "거래량 강한 순",
    sortModel: [{ colId: "volumeRatio", sort: "desc" }],
  },
  {
    value: "sector-asc",
    label: "섹터 이름순",
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
  volumeRatio: "거래량",
  relativeStrength: "상대강도",
  sector: "섹터",
  nextEvent: "다음 이벤트",
  thesis: "핵심 근거",
};

const compactColumns: RadarColumnKey[] = [
  "symbol",
  "name",
  "price",
  "changePercent",
  "score",
  "volumeRatio",
  "relativeStrength",
  "sector",
  "nextEvent",
  "thesis",
];

export function RadarWorkbench({ workspace }: RadarWorkbenchProps) {
  const { searchParams, replaceParams } = useUrlState();
  const [draftQuery, setDraftQuery] = React.useState(searchParams.get("q") ?? "");
  const [presetName, setPresetName] = React.useState("");
  const debouncedQuery = useDebouncedValue(draftQuery, 140);

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
  const activeFolderKey = React.useMemo(
    () => resolveActiveFolderKey(workspace.folders, folderId),
    [folderId, workspace.folders]
  );
  const sortModel =
    sortOptions.find((option) => option.value === sortValue)?.sortModel ??
    sortOptions[0].sortModel;

  const allTags = React.useMemo(
    () =>
      Array.from(
        new Set(workspace.rows.flatMap((row) => row.tags.map((tag) => tag.trim())))
      ).sort((left, right) => left.localeCompare(right, "ko-KR")),
    [workspace.rows]
  );

  const normalizedQuery = debouncedQuery.trim().toLowerCase();
  const filteredRows = React.useMemo(
    () => {
      const activeFolderSet =
        activeFolderKey.length > 0 ? new Set(activeFolderKey.split("|")) : null;

      return sortRadarRows(
        workspace.rows.filter((row) => {
          const matchesFolder = activeFolderSet
            ? activeFolderSet.has(row.folderId)
            : true;
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
    },
    [
      activeFolderKey,
      normalizedQuery,
      selectedSectorParam,
      sortModel,
      viewMode,
      workspace.rows,
    ]
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
  const activeAlertRuleCount = workspace.alertRules.filter(
    (rule) => rule.enabledByDefault
  ).length;
  const symbolAlerts = selectedRow
    ? workspace.detectedAlerts.filter((alert) => alert.symbol === selectedRow.symbol)
    : [];
  const visibleAlerts = (symbolAlerts.length > 0
    ? symbolAlerts
    : workspace.detectedAlerts
  ).slice(0, 4);
  const selectedPreset = presets.find(
    (preset) => preset.id === searchParams.get("preset")
  );
  const selectedVisibleColumns = compactColumns.filter((column) =>
    visibleColumns.includes(column)
  );

  const currentViewState: RadarViewPresetState = {
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
    <div className={layoutTokens.page} data-testid="radar-page">
      <section className="space-y-4">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-4xl">
            <p className={typographyTokens.eyebrow}>Radar</p>
            <h2 className={typographyTokens.title}>
              미국장과 국내장을 한 화면에서 빠르게 걸러보기
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              관심 종목을 가격, 거래량, 상대강도, 일정, 이슈 기준으로 좁혀 봅니다.
              종목을 고르면 오른쪽에 확인해야 할 근거와 알림이 바로 정리됩니다.
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="relative min-w-[260px]">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                data-testid="radar-search-input"
                value={draftQuery}
                onChange={(event) => setDraftQuery(event.target.value)}
                placeholder="티커, 종목명, 섹터, 태그 검색"
                className="pl-9"
              />
            </div>
            <Button
              type="button"
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
              <RotateCcw className="size-4" />
              초기화
            </Button>
          </div>
        </div>
        <DataSourceNotice source={workspace.dataSource} className="max-w-3xl" />
      </section>

      <div className={layoutTokens.threePanelGrid}>
        <ResearchPanel
          title="필터"
          description="폴더, 섹터, 태그, 저장된 보기를 조합합니다."
        >
          <div className="space-y-5">
            <div className="space-y-3">
              <p className={typographyTokens.eyebrow}>보기 방식</p>
              <FilterChipGroup
                options={groupModeOptions}
                value={groupMode}
                onValueChange={(value) =>
                  replaceParams({ group: value, preset: undefined })
                }
              />
            </div>

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
              <p className={typographyTokens.eyebrow}>섹터</p>
              <div className="flex flex-wrap gap-2">
                <TagChip
                  active={selectedSectorParam.length === 0}
                  label="전체"
                  onClick={() => replaceParams({ sector: undefined, preset: undefined })}
                />
                {workspace.sectorCards.map((sector) => (
                  <TagChip
                    key={sector.sector}
                    active={selectedSectorParam === sector.sector}
                    label={sector.sector}
                    onClick={() =>
                      replaceParams({
                        sector: sector.sector,
                        symbol: undefined,
                        preset: undefined,
                      })
                    }
                  />
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <p className={typographyTokens.eyebrow}>태그</p>
              <div className="flex flex-wrap gap-2">
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
              <p className={typographyTokens.eyebrow}>저장된 보기</p>
              <div className="flex gap-2">
                <Input
                  value={presetName}
                  onChange={(event) => setPresetName(event.target.value)}
                  placeholder="보기 이름"
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
                    onApply={() => applyPreset({ preset, replaceParams })}
                    onRemove={() => removePreset(preset.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="관심 종목"
          description={`${filteredRows.length}개 종목을 현재 조건으로 표시 중`}
          action={
            <span className="inline-flex items-center gap-1 rounded-md border border-border/70 bg-background px-2.5 py-1 text-xs font-semibold text-muted-foreground">
              <SlidersHorizontal className="size-3.5" />
              {viewMode === "core" ? "핵심" : viewMode === "volume" ? "거래량" : "변동성"}
            </span>
          }
        >
          <div className="space-y-4">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <FilterChipGroup
                options={radarModeOptions}
                value={viewMode}
                onValueChange={(value) =>
                  replaceParams({ view: value, preset: undefined })
                }
              />
              <Select
                value={sortValue}
                onValueChange={(value) =>
                  replaceParams({ sort: value, preset: undefined })
                }
              >
                <SelectTrigger className="w-full bg-background/65 sm:w-[180px]">
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
            </div>

            {groupMode === "flat" ? (
              <RadarTable
                rows={filteredRows}
                columns={selectedVisibleColumns}
                selectedSymbol={selectedRow?.symbol}
                onSelect={(row) =>
                  replaceParams({
                    symbol: row.symbol,
                    sector: row.sector,
                    preset: undefined,
                  })
                }
              />
            ) : (
              <div className="space-y-4">
                {groupedRows.map(([sector, rows]) => (
                  <div key={sector} className="space-y-2">
                    <button
                      type="button"
                      onClick={() =>
                        replaceParams({
                          sector,
                          symbol: rows[0]?.symbol,
                          preset: undefined,
                        })
                      }
                      className="flex w-full items-center justify-between rounded-md px-1 py-1 text-left hover:text-primary"
                    >
                      <span className="text-sm font-semibold">{sector}</span>
                      <span className="text-xs text-muted-foreground">
                        {rows.length}개 종목
                      </span>
                    </button>
                    <RadarTable
                      rows={rows}
                      columns={selectedVisibleColumns}
                      selectedSymbol={selectedRow?.symbol}
                      compact
                      onSelect={(row) =>
                        replaceParams({
                          symbol: row.symbol,
                          sector: row.sector,
                          preset: undefined,
                        })
                      }
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
              title={`${selectedRow.symbol} 점검`}
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
                <div className="rounded-lg border border-border/55 bg-background/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className={typographyTokens.eyebrow}>{selectedRow.sector}</p>
                      <p className="mt-1 text-base font-semibold">
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
                      label="거래량"
                      value={`${selectedRow.volumeRatio.toFixed(2)}x`}
                    />
                    <Metric
                      label="상대강도"
                      value={`${selectedRow.relativeStrength}`}
                    />
                    <Metric label="이벤트" value={selectedRow.nextEvent} />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Button asChild className="w-full">
                    <Link
                      href={`/stocks/${selectedRow.symbol}`}
                      data-testid="radar-open-selected-stock"
                    >
                      종목 분석 열기
                    </Link>
                  </Button>
                  <Button asChild variant="outline" className="w-full">
                    <Link href={`/history?symbol=${selectedRow.symbol}`}>
                      과거 이벤트 보기
                    </Link>
                  </Button>
                </div>
              </div>
            </ResearchPanel>
          ) : null}

          <ResearchPanel
            title="감지 알림"
            description={`${activeAlertRuleCount}개 규칙으로 우선 확인할 신호를 보여줍니다.`}
          >
            <div className="space-y-3" data-testid="radar-alert-panel">
              {visibleAlerts.length > 0 ? (
                visibleAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    ruleLabel={getAlertRuleLabel(workspace, alert.ruleId)}
                  />
                ))
              ) : (
                <p className="text-sm leading-6 text-muted-foreground">
                  현재 조건에 걸린 알림이 없습니다.
                </p>
              )}
            </div>
          </ResearchPanel>

          <SectorSummaryPanel
            title="섹터 요약"
            description={`${activeSector || "선택 없음"} 기준으로 필요한 맥락을 정리합니다.`}
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
            <ResearchPanel title="섹터 근거" description={selectedSectorCard.sector}>
              <div className="space-y-3">
                <p className="text-sm leading-6 text-muted-foreground">
                  {selectedSectorCard.thesis}
                </p>
                <Metric label="촉매" value={selectedSectorCard.catalyst} />
                <Button asChild variant="outline" className="w-full">
                  <Link href={`/stocks/${selectedSectorCard.topPick}`}>
                    Top Pick {selectedSectorCard.topPick}
                  </Link>
                </Button>
              </div>
            </ResearchPanel>
          ) : null}

          <ResearchPanel title="리포트" description={`${activeSector} 관련 메모`}>
            <div className="space-y-3">
              {selectedReports.map((report) => (
                <SmallCard key={`${report.house}-${report.symbol}`}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold">
                      {report.house} · {report.symbol}
                    </p>
                    <span className="text-xs text-muted-foreground">{report.stance}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {report.summary}
                  </p>
                </SmallCard>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="일정" description="선택한 섹터의 확인 일정">
            <div className="space-y-3">
              {selectedSchedules.map((schedule) => (
                <ScheduleRow key={`${schedule.time}-${schedule.title}`} schedule={schedule} />
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="주요 이슈" description="관련 뉴스와 공시 흐름">
            <div className="space-y-3">
              {selectedIssues.map((issue) => (
                <SmallCard key={issue.id}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold">{issue.headline}</p>
                    <span className="text-xs text-muted-foreground">
                      {issue.impactLabel}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {issue.summary}
                  </p>
                </SmallCard>
              ))}
            </div>
          </ResearchPanel>

          <ResearchPanel title="Top Pick" description="현재 조건에서 먼저 볼 종목">
            <div className="space-y-3">
              {selectedTopPicks.map((topPick) => (
                <Link
                  key={topPick.symbol}
                  href={`/stocks/${topPick.symbol}`}
                  className="flex items-center justify-between gap-3 rounded-lg border border-border/55 bg-background/30 p-3 transition-colors hover:bg-muted/60"
                >
                  <div>
                    <p className="text-sm font-semibold">{topPick.symbol}</p>
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

function RadarTable({
  rows,
  columns,
  selectedSymbol,
  compact,
  onSelect,
}: {
  rows: WatchlistRow[];
  columns: RadarColumnKey[];
  selectedSymbol?: string;
  compact?: boolean;
  onSelect: (row: WatchlistRow) => void;
}) {
  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border/70 px-4 py-10 text-center text-sm text-muted-foreground">
        조건에 맞는 종목이 없습니다.
      </div>
    );
  }

  return (
    <div
      className={cn(
        "overflow-hidden rounded-lg border border-border/70",
        compact ? "max-h-[340px]" : "max-h-[620px]"
      )}
    >
      <div className="overflow-x-auto">
        <table className="w-full min-w-[860px] border-collapse text-sm">
          <thead className="sticky top-0 z-10 bg-muted/80 backdrop-blur">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  scope="col"
                  className={cn(
                    "border-b border-border/70 px-3 py-2 text-left text-xs font-semibold text-muted-foreground",
                    numericColumns.has(column) ? "text-right" : undefined
                  )}
                >
                  {columnLabelMap[column]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.symbol}
                className={cn(
                  "border-b border-border/45 last:border-b-0",
                  row.symbol === selectedSymbol ? "bg-primary/10" : "hover:bg-muted/45"
                )}
              >
                {columns.map((column) => (
                  <td
                    key={`${row.symbol}-${column}`}
                    className={cn(
                      "px-3 py-3 align-top",
                      numericColumns.has(column) ? "numeric text-right" : undefined
                    )}
                  >
                    {renderCell({ row, column, onSelect })}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const numericColumns = new Set<RadarColumnKey>([
  "price",
  "changePercent",
  "score",
  "volumeRatio",
  "relativeStrength",
]);

function renderCell({
  row,
  column,
  onSelect,
}: {
  row: WatchlistRow;
  column: RadarColumnKey;
  onSelect: (row: WatchlistRow) => void;
}) {
  switch (column) {
    case "symbol":
      return (
        <button
          type="button"
          onClick={() => onSelect(row)}
          className="numeric font-semibold text-primary hover:underline"
        >
          {row.symbol}
        </button>
      );
    case "name":
      return (
        <div>
          <p className="font-medium">{row.name}</p>
          <p className="numeric mt-1 text-xs text-muted-foreground">
            {row.securityCode}
          </p>
        </div>
      );
    case "securityCode":
      return row.securityCode;
    case "price":
      return formatPrice(row.price);
    case "changePercent":
      return (
        <span
          className={cn(
            "numeric font-semibold",
            row.changePercent > 0
              ? "tone-positive"
              : row.changePercent < 0
                ? "tone-negative"
                : "tone-neutral"
          )}
        >
          {formatSignedPercent(row.changePercent)}
        </span>
      );
    case "score":
      return row.score;
    case "volumeRatio":
      return `${row.volumeRatio.toFixed(2)}x`;
    case "relativeStrength":
      return row.relativeStrength;
    case "sector":
      return row.sector;
    case "nextEvent":
      return row.nextEvent;
    case "thesis":
      return <span className="block max-w-[360px] leading-6">{row.thesis}</span>;
    default:
      return null;
  }
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

function resolveActiveFolderKey(
  folders: WatchlistFolderNode[],
  activeFolderId: string
) {
  if (activeFolderId === "all") {
    return "";
  }

  const targetNode = findFolderNode(folders, activeFolderId);

  if (!targetNode) {
    return "";
  }

  return collectFolderIds(targetNode).sort().join("|");
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

function getAlertRuleLabel(workspace: RadarFixture, ruleId: string) {
  return workspace.alertRules.find((rule) => rule.id === ruleId)?.label;
}

function AlertCard({
  alert,
  ruleLabel,
}: {
  alert: RadarDetectedAlert;
  ruleLabel?: string;
}) {
  return (
    <Link
      href={`/stocks/${alert.symbol}`}
      data-testid="radar-alert-card"
      className={cn(
        "block rounded-lg border bg-background/30 p-3 transition-colors hover:bg-muted/60",
        getAlertBorderClassName(alert.severity)
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold">{alert.title}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {ruleLabel ?? alert.ruleId} · {formatAlertTriggeredAt(alert.triggeredAt)}
          </p>
        </div>
        <span
          className={cn(
            "shrink-0 rounded-md px-2 py-0.5 text-[0.68rem] font-semibold",
            getAlertPillClassName(alert.severity)
          )}
        >
          {getAlertSeverityLabel(alert.severity)}
        </span>
      </div>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{alert.summary}</p>
    </Link>
  );
}

function getAlertSeverityLabel(severity: RadarDetectedAlert["severity"]) {
  if (severity === "critical") {
    return "주의";
  }

  if (severity === "watch") {
    return "관찰";
  }

  return "정보";
}

function getAlertBorderClassName(severity: RadarDetectedAlert["severity"]) {
  if (severity === "critical") {
    return "border-[color:color-mix(in_oklch,var(--negative)_28%,var(--border))]";
  }

  if (severity === "watch") {
    return "border-[color:color-mix(in_oklch,var(--primary)_28%,var(--border))]";
  }

  return "border-border/55";
}

function getAlertPillClassName(severity: RadarDetectedAlert["severity"]) {
  if (severity === "critical") {
    return "bg-[color:color-mix(in_oklch,var(--negative)_16%,transparent)] text-[var(--negative)]";
  }

  if (severity === "watch") {
    return "bg-primary/10 text-primary";
  }

  return "bg-muted text-muted-foreground";
}

function formatAlertTriggeredAt(value: string) {
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);

  if (!match) {
    return value;
  }

  return `${match[2]}.${match[3]} ${match[4]}:${match[5]}`;
}

function applyPreset({
  preset,
  replaceParams,
}: {
  preset: SavedViewPreset<RadarViewPresetState>;
  replaceParams: (updates: Record<string, string | null | undefined>) => void;
}) {
  const matchedSortOption =
    sortOptions.find(
      (option) =>
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
    <div className="rounded-lg border border-border/50 bg-background/40 px-3 py-2">
      <p className={typographyTokens.eyebrow}>{label}</p>
      <p className="numeric mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}

function SmallCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border/55 bg-background/30 p-3">
      {children}
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
        "rounded-md border px-2.5 py-1 text-xs font-semibold transition-colors",
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
    <div className="flex items-start justify-between gap-3 rounded-lg border border-border/55 bg-background/30 p-3">
      <div>
        <p className="text-sm font-semibold">{schedule.title}</p>
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
  preset: SavedViewPreset<RadarViewPresetState>;
  active: boolean;
  onApply: () => void;
  onRemove: () => void;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border p-3",
        active ? "border-primary/35 bg-primary/10" : "border-border/60 bg-background/30"
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold">{preset.name}</p>
          <p className="text-xs text-muted-foreground">
            {formatPresetUpdatedAt(preset.updatedAt)}
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

function formatPresetUpdatedAt(value: string) {
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);

  if (!match) {
    return value;
  }

  return `${match[2]}.${match[3]} ${match[4]}:${match[5]}`;
}
