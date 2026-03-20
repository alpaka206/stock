"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { InstrumentSearch } from "@/components/research/instrument-search";
import { ResearchPanel } from "@/components/research/research-panel";
import { TrendChip } from "@/components/research/trend-chip";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResearchLineChart } from "@/features/chart/components/research-line-chart";
import { useRecentSymbols } from "@/lib/client/use-recent-symbols";
import { useStoredPresets } from "@/lib/client/use-stored-presets";
import { useUrlState } from "@/lib/client/use-url-state";
import type { SavedViewPreset, StockFixture, StockRulePresetState } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type StockDetailPageProps = {
  stock: StockFixture;
};

const stockTabs = [
  { value: "score", label: "점수" },
  { value: "flow", label: "수급" },
  { value: "short", label: "공매도/옵션" },
  { value: "issues", label: "이슈 분석" },
] as const;

export function StockDetailPage({ stock }: StockDetailPageProps) {
  const router = useRouter();
  const { searchParams, replaceParams } = useUrlState();
  const [presetName, setPresetName] = React.useState("");
  const [selectedMarkerId, setSelectedMarkerId] = React.useState(
    stock.eventMarkers[0]?.id ?? ""
  );

  const { symbols: recentSymbols, pushSymbol } = useRecentSymbols(
    "stock-workspace:recent-symbols",
    stock.relatedSymbols.slice(0, 3)
  );

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
      name: "기본 규칙",
      updatedAt: new Date().toISOString(),
      value: {
        presetId: "default",
        indicatorIds: defaultIndicatorIds,
      },
    }),
    [defaultIndicatorIds]
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
    stockTabs.find((item) => item.value === searchParams.get("tab"))?.value ?? "score";
  const activePresetId = searchParams.get("preset") ?? defaultPreset.id;
  const activePreset =
    presets.find((preset) => preset.id === activePresetId) ?? defaultPreset;
  const indicatorIds = parseIndicatorIds(
    searchParams.get("indicators"),
    activePreset.value.indicatorIds
  );
  const selectedMarker =
    stock.eventMarkers.find((marker) => marker.id === selectedMarkerId) ??
    stock.eventMarkers[0];
  const visibleGuides = stock.indicatorGuides.filter(
    (guide) => guide.enabled !== false && indicatorIds.includes(guide.id)
  );
  const direction =
    stock.changePercent > 0 ? "up" : stock.changePercent < 0 ? "down" : "flat";

  return (
    <div className={layoutTokens.page}>
      <div className="space-y-2">
        <p className={typographyTokens.eyebrow}>Stock Workstation</p>
        <h2 className={typographyTokens.title}>
          한 종목의 판단 근거를 차트 중심으로 모아 보는 분석 워크스테이션
        </h2>
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
                  label="빠른 전환"
                  helperText="티커, 종목명, 종목번호 검색으로 바로 다른 종목 워크스테이션으로 이동한다."
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
              <Metric label="현재가" value={stock.price.toFixed(2)} />
              <Metric label="시가총액" value={stock.instrument.marketCap} />
              <Metric label="핵심 해석" value={`${stock.scoreSummary.total}점`} />
            </div>

            <p className="text-sm leading-6 text-muted-foreground">{stock.thesis}</p>

            <ResearchLineChart
              points={stock.priceSeries}
              guides={visibleGuides}
              markers={stock.eventMarkers}
              activePointKey={selectedMarker?.date}
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
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="사용자 규칙 / preset"
          description="보조지표 6개 이상 규칙과 사용자 preset을 저장한다."
          className="h-fit"
        >
          <div className="space-y-4">
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

                  savePreset(trimmedName, {
                    presetId: trimmedName,
                    indicatorIds,
                  });
                  setPresetName("");
                }}
              >
                저장
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
                        {preset.value.indicatorIds.length}개 규칙
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
                        적용
                      </Button>
                      {preset.id !== "default" ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => removePreset(preset.id)}
                        >
                          삭제
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
                        {active ? "활성" : "보류"}
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
      </div>

      <Tabs
        value={activeTab}
        onValueChange={(value) => replaceParams({ tab: value })}
      >
        <TabsList variant="line" className="w-full justify-start overflow-x-auto">
          {stockTabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="score">
          <div className="grid gap-[var(--space-grid)] xl:grid-cols-[320px_minmax(0,1fr)]">
            <ResearchPanel
              title="총합 점수"
              description={stock.scoreSummary.confidence.rationale}
              className="h-fit"
            >
              <div className="space-y-3">
                <p className="numeric text-4xl font-semibold">
                  {stock.scoreSummary.total}
                </p>
                <p className="text-sm leading-6 text-muted-foreground">
                  confidence {stock.scoreSummary.confidence.score.toFixed(2)} ·{" "}
                  {stock.scoreSummary.confidence.label}
                </p>
              </div>
            </ResearchPanel>
            <div className="grid gap-[var(--space-grid)] md:grid-cols-2">
              {stock.scoreSummary.breakdown.map((item) => (
                <ResearchPanel
                  key={item.label}
                  title={item.label}
                  description={`${item.score}점`}
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
            title="수급 요약"
            items={stock.flowMetrics}
            unavailable={stock.flowUnavailable}
          />
        </TabsContent>

        <TabsContent value="short">
          <MetricGrid
            title="공매도/옵션 비율"
            items={stock.optionsShortMetrics}
            unavailable={stock.optionsUnavailable}
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
                    <Link href={issue.href}>관련 화면으로 이동</Link>
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

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4">
      <p className={typographyTokens.eyebrow}>{label}</p>
      <p className="numeric mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function MetricGrid({
  title,
  items,
  unavailable,
}: {
  title: string;
  items: Array<{ label: string; value: string; detail: string; tone: string }>;
  unavailable?: { label: string; reason: string; expectedSource?: string };
}) {
  return (
    <div className="space-y-4">
      {unavailable ? (
        <ResearchPanel title={unavailable.label} description={title} className="h-fit">
          <p className="text-sm leading-6 text-muted-foreground">{unavailable.reason}</p>
          {unavailable.expectedSource ? (
            <p className="mt-2 text-xs text-muted-foreground">
              예상 source: {unavailable.expectedSource}
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
