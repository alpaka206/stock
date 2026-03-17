"use client";

import Link from "next/link";

import { ResearchPanel } from "@/components/research/research-panel";
import { TrendChip } from "@/components/research/trend-chip";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResearchLineChart } from "@/features/chart/components/research-line-chart";
import type { StockFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type StockDetailPageProps = {
  stock: StockFixture;
};

export function StockDetailPage({ stock }: StockDetailPageProps) {
  const direction =
    stock.changePercent > 0 ? "up" : stock.changePercent < 0 ? "down" : "flat";

  return (
    <div className={layoutTokens.page}>
      <div className="space-y-2">
        <p className={typographyTokens.eyebrow}>Stock Detail</p>
        <h2 className={typographyTokens.title}>
          차트, 수급, 옵션·공매도, 점수를 한 흐름으로 읽는 종목 분석 스테이션
        </h2>
      </div>

      <div className={layoutTokens.splitPanelGrid}>
        <ResearchPanel
          title={`${stock.symbol} · ${stock.name}`}
          description={`${stock.exchange} · 시가총액 ${stock.marketCap}`}
          action={<TrendChip direction={direction} value={stock.changePercent} />}
        >
          <div className="space-y-4">
            <div className="flex flex-col gap-3 rounded-[calc(var(--radius)*1.1)] border border-border/55 bg-background/30 p-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex flex-wrap items-center gap-3">
                <Input
                  value={stock.symbol}
                  readOnly
                  className="w-[140px] bg-background/75"
                />
                <p className="text-sm text-muted-foreground">
                  샘플 심볼 프리셋으로 구조를 확인한다.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {stock.relatedSymbols.map((symbol) => (
                  <Button key={symbol} asChild variant="outline" size="sm">
                    <Link href={`/stocks/${symbol}`}>{symbol}</Link>
                  </Button>
                ))}
              </div>
            </div>

            <p className="text-sm leading-6 text-muted-foreground">
              {stock.thesis}
            </p>

            <ResearchLineChart
              points={stock.chartPoints}
              guides={stock.indicatorGuides}
              accent="primary"
            />
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="규칙 프리셋"
          description="보조지표와 무효화 조건을 오른쪽 패널에 고정"
          className="h-fit"
        >
          <div className="space-y-3">
            {stock.rulePresets.map((preset) => (
              <div
                key={preset.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">
                    {preset.label}
                  </p>
                  <span
                    className={cn(
                      "rounded-full px-2 py-1 text-[0.68rem] font-semibold",
                      preset.enabled
                        ? "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    {preset.enabled ? "활성" : "보류"}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {preset.description}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            {stock.indicatorGuides.map((guide) => (
              <div
                key={guide.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
              >
                <p className={typographyTokens.eyebrow}>{guide.label}</p>
                <p className="numeric mt-2 text-lg font-semibold">
                  {guide.value.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </ResearchPanel>
      </div>

      <Tabs defaultValue="score">
        <TabsList variant="line" className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="score">점수</TabsTrigger>
          <TabsTrigger value="flow">수급</TabsTrigger>
          <TabsTrigger value="short">옵션·공매도</TabsTrigger>
          <TabsTrigger value="issues">이슈</TabsTrigger>
        </TabsList>

        <TabsContent value="score">
          <div className="grid gap-[var(--space-grid)] lg:grid-cols-3">
            {stock.scoreBreakdown.map((item) => (
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
        </TabsContent>

        <TabsContent value="flow">
          <div className="grid gap-[var(--space-grid)] md:grid-cols-3">
            {stock.flows.map((flow) => (
              <ResearchPanel key={flow.label} title={flow.label} description={flow.delta}>
                <p className="numeric text-2xl font-semibold">{flow.value}</p>
                <p
                  className={cn(
                    "mt-2 text-xs font-semibold uppercase tracking-[0.16em]",
                    flow.tone === "positive"
                      ? "tone-positive"
                      : flow.tone === "negative"
                        ? "tone-negative"
                        : "tone-neutral"
                  )}
                >
                  {flow.delta}
                </p>
              </ResearchPanel>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="short">
          <div className="grid gap-[var(--space-grid)] md:grid-cols-3">
            {stock.shortOptionMetrics.map((metric) => (
              <ResearchPanel
                key={metric.label}
                title={metric.label}
                description={metric.detail}
              >
                <p className="numeric text-2xl font-semibold">{metric.value}</p>
              </ResearchPanel>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="issues">
          <div className="grid gap-[var(--space-grid)] lg:grid-cols-2">
            {stock.issues.map((issue) => (
              <ResearchPanel key={issue.title} title={issue.title} description={issue.source}>
                <p className="text-sm leading-6 text-muted-foreground">
                  {issue.summary}
                </p>
              </ResearchPanel>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
