"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAppLanguage } from "@/components/providers/language-provider";
import { DataSourceNotice } from "@/components/research/data-source-notice";
import { InstrumentSearch } from "@/components/research/instrument-search";
import { ResearchPanel } from "@/components/research/research-panel";
import { ResearchSnapshotCard } from "@/components/research/research-snapshot-card";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResearchLineChart } from "@/features/chart/components/research-line-chart";
import { useRecentSymbols } from "@/lib/client/use-recent-symbols";
import {
  researchSnapshotConvictionValues,
  researchSnapshotStanceValues,
  useResearchSnapshots,
} from "@/lib/client/use-research-snapshots";
import { useStoredPresets } from "@/lib/client/use-stored-presets";
import { useUrlState } from "@/lib/client/use-url-state";
import type {
  ResearchSnapshotConviction,
  ResearchSnapshotStance,
  SavedViewPreset,
  StockFixture,
  StockRulePresetState,
} from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type StockDetailPageProps = {
  stock: StockFixture;
};

const stockTabs = ["score", "flow", "short", "issues"] as const;

export function StockDetailPage({ stock }: StockDetailPageProps) {
  const router = useRouter();
  const { language, messages } = useAppLanguage();
  const stockMessages = messages.stocks.detail;
  const { searchParams, replaceParams } = useUrlState();
  const [presetName, setPresetName] = React.useState("");
  const [selectedMarkerId, setSelectedMarkerId] = React.useState(
    stock.eventMarkers[0]?.id ?? ""
  );
  const [snapshotStance, setSnapshotStance] =
    React.useState<ResearchSnapshotStance>("neutral");
  const [snapshotConviction, setSnapshotConviction] =
    React.useState<ResearchSnapshotConviction>("medium");
  const [snapshotNote, setSnapshotNote] = React.useState("");

  const { symbols: recentSymbols, pushSymbol } = useRecentSymbols(
    "stock-workspace:recent-symbols",
    stock.relatedSymbols.slice(0, 3)
  );
  const { snapshots, saveSnapshot, removeSnapshot } = useResearchSnapshots();

  const defaultIndicatorIds = React.useMemo(
    () =>
      stock.rulePresetDefinitions
        .filter((definition) => definition.enabledByDefault)
        .map((definition) => definition.id),
    [stock.rulePresetDefinitions]
  );

  const defaultPreset: SavedViewPreset<StockRulePresetState> = React.useMemo(
    () => ({
      id: "default",
      name: language === "en" ? "Default Rules" : "기본 규칙",
      updatedAt: new Date().toISOString(),
      value: {
        presetId: "default",
        indicatorIds: defaultIndicatorIds,
      },
    }),
    [defaultIndicatorIds, language]
  );

  const { presets, savePreset, removePreset } = useStoredPresets(
    `stock-workspace:stock-presets:${stock.instrument.symbol}`,
    [defaultPreset]
  );

  React.useEffect(() => {
    setSelectedMarkerId(stock.eventMarkers[0]?.id ?? "");
  }, [stock.eventMarkers]);

  React.useEffect(() => {
    pushSymbol(stock.instrument.symbol);
  }, [pushSymbol, stock.instrument.symbol]);

  const activeTab =
    stockTabs.find((item) => item === searchParams.get("tab")) ?? "score";
  const activePresetId = searchParams.get("preset") ?? defaultPreset.id;
  const activePreset =
    presets.find((preset) => preset.id === activePresetId) ?? defaultPreset;
  const indicatorIds = parseIndicatorIds(
    searchParams.get("indicators"),
    activePreset.value.indicatorIds
  );
  const activeRuleDefinitions = stock.rulePresetDefinitions.filter((definition) =>
    indicatorIds.includes(definition.id)
  );
  const visibleGuideIds = new Set(
    activeRuleDefinitions.flatMap((definition) => resolveRuleGuideIds(definition))
  );
  const hasEventMarkerRule = stock.rulePresetDefinitions.some(
    (definition) => definition.controlsEventMarkers || definition.id === "event-window"
  );
  const showEventMarkers = hasEventMarkerRule
    ? activeRuleDefinitions.some(
        (definition) => definition.controlsEventMarkers || definition.id === "event-window"
      )
    : true;
  const selectedMarker =
    stock.eventMarkers.find((marker) => marker.id === selectedMarkerId) ??
    stock.eventMarkers[0];
  const visibleGuides = stock.indicatorGuides.filter(
    (guide) => guide.enabled !== false && visibleGuideIds.has(guide.id)
  );
  const visibleOverlays = stock.chartOverlays.filter(
    (overlay) => overlay.enabled !== false && visibleGuideIds.has(overlay.id)
  );
  const direction =
    stock.changePercent > 0 ? "up" : stock.changePercent < 0 ? "down" : "flat";
  const symbolSnapshots = React.useMemo(
    () =>
      snapshots
        .filter((snapshot) => snapshot.symbol === stock.instrument.symbol)
        .slice(0, 3),
    [snapshots, stock.instrument.symbol]
  );
  const canSaveSnapshot = snapshotNote.trim().length > 0;
  const tabLabels = {
    score: messages.stocks.tabs.score,
    flow: messages.stocks.tabs.flow,
    short: messages.stocks.tabs.short,
    issues: messages.stocks.tabs.issues,
  } as const;

  return (
    <div className={layoutTokens.page} data-testid="stock-detail-page">
      <div className="space-y-3">
        <p className={typographyTokens.eyebrow}>{stockMessages.eyebrow}</p>
        <DataSourceNotice source={stock.dataSource} className="max-w-2xl" />
        <h2 className={typographyTokens.title}>{stockMessages.title}</h2>
      </div>

      <div className="grid gap-[var(--space-grid)] xl:grid-cols-[minmax(0,1.45fr)_360px]">
        <ResearchPanel
          title={`${stock.instrument.symbol} · ${stock.instrument.name}`}
          description={`${stock.instrument.exchange} · ${stock.instrument.securityCode} · ${stock.instrument.sector}`}
          action={<TrendChip direction={direction} value={stock.changePercent} />}
        >
          <div className="space-y-5">
            <div className="rounded-[calc(var(--radius)*1.1)] border border-border/55 bg-background/30 p-4">
              <div className="flex flex-col gap-4">
                <InstrumentSearch
                  selectedSymbol={stock.instrument.symbol}
                  label={stockMessages.quickSwitchLabel}
                  helperText={stockMessages.quickSwitchHelper}
                  quickSymbols={Array.from(
                    new Set([...recentSymbols, ...stock.relatedSymbols])
                  ).slice(0, 6)}
                  onSelect={(instrument) => {
                    router.push(`/stocks/${instrument.symbol}`);
                  }}
                />
                <div className="flex flex-wrap items-center gap-2">
                  {stock.relatedSymbols.map((symbol) => (
                    <Button key={symbol} asChild variant="outline" size="sm">
                      <Link href={`/stocks/${symbol}`}>{symbol}</Link>
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <Metric label={stockMessages.currentPrice} value={stock.price.toFixed(2)} />
              <Metric label={stockMessages.marketCap} value={stock.instrument.marketCap} />
              <Metric
                label={stockMessages.scoreView}
                value={`${stock.scoreSummary.total}${language === "en" ? "" : "점"}`}
              />
            </div>

            <p className="text-sm leading-6 text-muted-foreground">{stock.thesis}</p>

            <ResearchLineChart
              testId="stock-price-chart"
              points={stock.priceSeries}
              guides={visibleGuides}
              overlays={visibleOverlays}
              markers={showEventMarkers ? stock.eventMarkers : []}
              activePointKey={showEventMarkers ? selectedMarker?.date : undefined}
              onPointSelect={(pointKey) => {
                const matchedMarker = stock.eventMarkers.find(
                  (marker) => marker.date === pointKey || marker.pointLabel === pointKey
                );

                if (matchedMarker) {
                  setSelectedMarkerId(matchedMarker.id);
                }
              }}
              accent="primary"
            />

            <div className="grid gap-3 md:grid-cols-2">
              {stock.eventMarkers.map((marker) => (
                <button
                  key={marker.id}
                  type="button"
                  onClick={() => setSelectedMarkerId(marker.id)}
                  className={cn(
                    "rounded-[calc(var(--radius)*1.05)] border px-3 py-3 text-left transition-colors",
                    marker.id === selectedMarker?.id
                      ? "border-primary/35 bg-primary/10"
                      : "border-border/60 bg-background/25 hover:bg-muted/60"
                  )}
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold tracking-tight">{marker.title}</p>
                    <span className="text-xs text-muted-foreground">{marker.label}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{marker.date}</p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {marker.detail}
                  </p>
                </button>
              ))}
            </div>

            <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.9fr)]">
              <ResearchPanel
                title="기술 지표 체크"
                description="이동평균, 모멘텀, 거래량, 지지/저항을 실제 시계열로 계산합니다."
                size="sm"
              >
                <div
                  className="grid gap-2 sm:grid-cols-2"
                  data-testid="stock-technical-metrics"
                >
                  {stock.technicalMetrics.map((metric) => (
                    <div key={metric.id} data-testid="stock-technical-metric">
                      <Metric
                        label={metric.label}
                        value={metric.value}
                        detail={metric.detail}
                      />
                    </div>
                  ))}
                </div>
              </ResearchPanel>

              <ResearchPanel
                title="패턴 유사도"
                description="현재 차트 구조와 가까운 패턴, 진행 단계, 무효화 조건입니다."
                size="sm"
              >
                <div className="space-y-2" data-testid="stock-pattern-cards">
                  {stock.patternCards.slice(0, 3).map((pattern) => (
                    <div
                      key={pattern.id}
                      data-testid="stock-pattern-card"
                      className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 px-3 py-3"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold tracking-tight">
                          {pattern.label}
                        </p>
                        <span className="numeric text-xs font-semibold text-muted-foreground">
                          {Math.round(pattern.similarity * 100)}%
                        </span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {pattern.stage} · 무효화: {pattern.invalidation}
                      </p>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        {pattern.summary}
                      </p>
                    </div>
                  ))}
                </div>
              </ResearchPanel>
            </div>
          </div>
        </ResearchPanel>

        <div className="space-y-[var(--space-grid)]">
          <ResearchPanel
            title={stockMessages.rulesPresetTitle}
            description={stockMessages.rulesPresetDescription}
            className="h-fit"
          >
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={presetName}
                  onChange={(event) => setPresetName(event.target.value)}
                  placeholder={stockMessages.presetPlaceholder}
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

                    savePreset(trimmedName, {
                      presetId: trimmedName,
                      indicatorIds,
                    });
                    setPresetName("");
                  }}
                >
                  {messages.common.save}
                </Button>
              </div>

              <div className="space-y-2">
                {presets.map((preset) => (
                  <div
                    key={preset.id}
                    className={cn(
                      "rounded-[calc(var(--radius)*1.05)] border p-3",
                      preset.id === activePreset.id
                        ? "border-primary/35 bg-primary/10"
                        : "border-border/60 bg-background/30"
                    )}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold tracking-tight">{preset.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {preset.value.indicatorIds.length} {stockMessages.ruleCountSuffix}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            replaceParams({
                              preset: preset.id,
                              indicators: preset.value.indicatorIds.join(","),
                            })
                          }
                        >
                          {messages.common.apply}
                        </Button>
                        {preset.id !== "default" ? (
                          <Button
                            type="button"
                            size="sm"
                            variant="ghost"
                            onClick={() => removePreset(preset.id)}
                          >
                            {messages.common.delete}
                          </Button>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="space-y-3">
                {stock.rulePresetDefinitions.map((definition) => {
                  const active = indicatorIds.includes(definition.id);

                  return (
                    <button
                      key={definition.id}
                      type="button"
                      onClick={() => {
                        const nextIds = active
                          ? indicatorIds.filter((item) => item !== definition.id)
                          : [...indicatorIds, definition.id];

                        replaceParams({
                          indicators: nextIds.join(","),
                          preset: undefined,
                        });
                      }}
                      className={cn(
                        "w-full rounded-[calc(var(--radius)*1.05)] border px-4 py-3 text-left transition-colors",
                        active
                          ? "border-primary/35 bg-primary/10"
                          : "border-border/60 bg-background/25 hover:bg-muted/60"
                      )}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold tracking-tight">
                          {definition.label}
                        </p>
                        <span className="text-xs text-muted-foreground">
                          {active ? messages.common.active : messages.common.inactive}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        {definition.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          </ResearchPanel>

          <ResearchPanel
            title={stockMessages.snapshotTitle}
            description={stockMessages.snapshotDescription}
            className="h-fit"
          >
            <div className="space-y-4">
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-1">
                <Select
                  value={snapshotStance}
                  onValueChange={(value) =>
                    setSnapshotStance(value as ResearchSnapshotStance)
                  }
                >
                  <SelectTrigger className="w-full bg-background/65">
                    <SelectValue placeholder={stockMessages.stancePlaceholder} />
                  </SelectTrigger>
                  <SelectContent>
                    {researchSnapshotStanceValues.map((value) => (
                      <SelectItem key={value} value={value}>
                        {messages.stocks.stance[value]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select
                  value={snapshotConviction}
                  onValueChange={(value) =>
                    setSnapshotConviction(value as ResearchSnapshotConviction)
                  }
                >
                  <SelectTrigger className="w-full bg-background/65">
                    <SelectValue placeholder={stockMessages.convictionPlaceholder} />
                  </SelectTrigger>
                  <SelectContent>
                    {researchSnapshotConvictionValues.map((value) => (
                      <SelectItem key={value} value={value}>
                        {messages.stocks.conviction[value]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <textarea
                value={snapshotNote}
                onChange={(event) => setSnapshotNote(event.target.value)}
                placeholder={stockMessages.snapshotNotePlaceholder}
                rows={4}
                className="min-h-28 w-full rounded-[calc(var(--radius)*1.05)] border border-border/60 bg-background/70 px-3 py-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-primary/35"
              />

              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-muted-foreground">
                  {stockMessages.snapshotMeta
                    .replace("{event}", selectedMarker?.title ?? messages.common.none)
                    .replace("{count}", String(activeRuleDefinitions.length))}
                </p>
                <div className="flex items-center gap-2">
                  <Button asChild variant="outline" size="sm">
                    <Link href={`/history?symbol=${stock.instrument.symbol}`}>
                      {stockMessages.viewHistory}
                    </Link>
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    disabled={!canSaveSnapshot}
                    onClick={() => {
                      const trimmedNote = snapshotNote.trim();

                      if (!trimmedNote) {
                        return;
                      }

                      saveSnapshot({
                        symbol: stock.instrument.symbol,
                        name: stock.instrument.name,
                        exchange: stock.instrument.exchange,
                        securityCode: stock.instrument.securityCode,
                        sector: stock.instrument.sector,
                        note: trimmedNote,
                        stance: snapshotStance,
                        conviction: snapshotConviction,
                        price: stock.price,
                        changePercent: stock.changePercent,
                        score: stock.scoreSummary.total,
                        thesis: stock.thesis,
                        selectedEventTitle: selectedMarker?.title,
                        selectedEventDate: selectedMarker?.date,
                        activeRuleLabels: activeRuleDefinitions.map(
                          (definition) => definition.label
                        ),
                        presetName: activePreset.name,
                      });
                      setSnapshotNote("");
                      setSnapshotStance("neutral");
                      setSnapshotConviction("medium");
                    }}
                  >
                    {stockMessages.saveSnapshot}
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                {symbolSnapshots.length > 0 ? (
                  symbolSnapshots.map((snapshot) => (
                    <ResearchSnapshotCard
                      key={snapshot.id}
                      snapshot={snapshot}
                      compact
                      actions={
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => removeSnapshot(snapshot.id)}
                        >
                          {messages.common.delete}
                        </Button>
                      }
                    />
                  ))
                ) : (
                  <div className="rounded-[calc(var(--radius)*1.05)] border border-dashed border-border/60 px-4 py-5 text-sm leading-6 text-muted-foreground">
                    {stockMessages.emptySnapshots}
                  </div>
                )}
              </div>
            </div>
          </ResearchPanel>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => replaceParams({ tab: value })}>
        <TabsList variant="line" className="w-full justify-start overflow-x-auto">
          {stockTabs.map((tab) => (
            <TabsTrigger key={tab} value={tab}>
              {tabLabels[tab]}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="score">
          <div className="grid gap-[var(--space-grid)] xl:grid-cols-[320px_minmax(0,1fr)]">
            <ResearchPanel
              title={stockMessages.scoreSummaryTitle}
              description={stock.scoreSummary.confidence.rationale}
              className="h-fit"
            >
              <div className="space-y-3">
                <p className="numeric text-4xl font-semibold">{stock.scoreSummary.total}</p>
                <p className="text-sm leading-6 text-muted-foreground">
                  {messages.common.confidence}{" "}
                  {stock.scoreSummary.confidence.score.toFixed(2)} ·{" "}
                  {
                    messages.stocks.conviction[
                      stock.scoreSummary.confidence.label as ResearchSnapshotConviction
                    ]
                  }
                </p>
              </div>
            </ResearchPanel>
            <div className="grid gap-[var(--space-grid)] md:grid-cols-2">
              {stock.scoreSummary.breakdown.map((item) => (
                <ResearchPanel
                  key={item.label}
                  title={item.label}
                  description={`${item.score}${stockMessages.scoreItemSuffix}`}
                  size="sm"
                >
                  <p className="text-sm leading-6 text-muted-foreground">
                    {item.summary}
                  </p>
                </ResearchPanel>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="flow">
          <MetricGrid
            title={stockMessages.flowSummaryTitle}
            items={stock.flowMetrics}
            unavailable={stock.flowUnavailable}
            expectedSourceLabel={messages.common.expectedSource}
          />
        </TabsContent>

        <TabsContent value="short">
          <MetricGrid
            title={stockMessages.shortSummaryTitle}
            items={stock.optionsShortMetrics}
            unavailable={stock.optionsUnavailable}
            expectedSourceLabel={messages.common.expectedSource}
          />
        </TabsContent>

        <TabsContent value="issues">
          <div className="grid gap-[var(--space-grid)] lg:grid-cols-2">
            {stock.issues.map((issue) => (
              <ResearchPanel key={issue.title} title={issue.title} description={issue.source}>
                <p className="text-sm leading-6 text-muted-foreground">
                  {issue.summary}
                </p>
                {issue.href ? (
                  <Button asChild variant="link" className="mt-2 h-auto px-0">
                    <Link href={issue.href}>{stockMessages.issueLink}</Link>
                  </Button>
                ) : null}
              </ResearchPanel>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function resolveRuleGuideIds(
  definition: StockFixture["rulePresetDefinitions"][number]
) {
  if (definition.guideIds && definition.guideIds.length > 0) {
    return definition.guideIds;
  }

  switch (definition.id) {
    case "ma-trend":
      return ["ma5", "ma20", "ma60", "ma120"];
    case "support-hold":
      return ["support"];
    case "trend-base":
      return ["trend-base"];
    case "volume-spike":
      return ["volume-spike", "volume"];
    case "relative-strength":
      return ["relative-strength"];
    case "volatility-guard":
      return ["volatility-guard", "volatility"];
    default:
      return [];
  }
}

function parseIndicatorIds(value: string | null, fallback: string[]) {
  if (!value) {
    return fallback;
  }

  const parsed = value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return parsed.length > 0 ? parsed : fallback;
}

function Metric({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4">
      <p className={typographyTokens.eyebrow}>{label}</p>
      <p className="numeric mt-2 text-2xl font-semibold">{value}</p>
      {detail ? (
        <p className="mt-2 text-xs leading-5 text-muted-foreground">{detail}</p>
      ) : null}
    </div>
  );
}

function MetricGrid({
  title,
  items,
  unavailable,
  expectedSourceLabel,
}: {
  title: string;
  items: Array<{ label: string; value: string; detail: string; tone: string }>;
  unavailable?: { label: string; reason: string; expectedSource?: string } | null;
  expectedSourceLabel: string;
}) {
  return (
    <div className="space-y-4">
      {unavailable ? (
        <ResearchPanel title={unavailable.label} description={title} className="h-fit">
          <p className="text-sm leading-6 text-muted-foreground">{unavailable.reason}</p>
          {unavailable.expectedSource ? (
            <p className="mt-2 text-xs text-muted-foreground">
              {expectedSourceLabel}: {unavailable.expectedSource}
            </p>
          ) : null}
        </ResearchPanel>
      ) : null}
      <div className="grid gap-[var(--space-grid)] md:grid-cols-3">
        {items.map((item) => (
          <ResearchPanel key={item.label} title={item.label} description={item.detail}>
            <p className="numeric text-2xl font-semibold">{item.value}</p>
          </ResearchPanel>
        ))}
      </div>
    </div>
  );
}
