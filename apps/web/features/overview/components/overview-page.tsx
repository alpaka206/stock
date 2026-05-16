import Link from "next/link";
import {
  Activity,
  ArrowRight,
  CalendarDays,
  Clock3,
  Database,
  History,
  Newspaper,
  Radar,
  type LucideIcon,
} from "lucide-react";

import { DataSourceNotice } from "@/components/research/data-source-notice";
import { AiMarketSummaryCard } from "@/features/overview/components/ai-market-summary-card";
import { IndexStrip } from "@/features/overview/components/index-strip";
import { MarketHeatmap } from "@/features/overview/components/market-heatmap";
import { NewsPanel } from "@/features/overview/components/news-panel";
import { RiskBanner } from "@/features/overview/components/risk-banner";
import { SectorStrengthPanel } from "@/features/overview/components/sector-strength-panel";
import type { OverviewFixture } from "@/lib/research/types";
import { layoutTokens, surfaceStyles, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type OverviewPageProps = {
  data: OverviewFixture;
};

type Tone = "positive" | "negative" | "neutral";

export function OverviewPage({ data }: OverviewPageProps) {
  const marketState = getMarketState(data);
  const dataState = getDataState(data);

  return (
    <div className={layoutTokens.page} data-testid="overview-page">
      <section className={cn(surfaceStyles.panel, "overflow-hidden p-[var(--card-padding)]")}>
        <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="min-w-0">
            <div className="flex flex-wrap gap-2">
              <StatusPill
                icon={Activity}
                label="시장 상태"
                value={marketState.label}
                tone={marketState.tone}
              />
              <StatusPill
                icon={Clock3}
                label="업데이트"
                value={data.asOf}
                tone="neutral"
              />
              <StatusPill
                icon={Database}
                label="데이터"
                value={dataState.label}
                tone={dataState.tone}
              />
            </div>

            <div className="mt-5 max-w-4xl">
              <p className={typographyTokens.eyebrow}>오늘 먼저 볼 것</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-normal lg:text-[2rem]">
                지수보다 주도 섹터와 리스크를 먼저 확인하세요.
              </h2>
              <p className="mt-3 text-sm leading-7 text-muted-foreground lg:text-[0.96rem]">
                초보자는 가격만 보면 이유를 놓치기 쉽습니다. 이 화면은 시장 방향,
                섹터 강도, 뉴스, 공시, 리스크를 먼저 묶어서 다음 행동으로 이어지게
                설계했습니다.
              </p>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-3">
              <DeskMetric
                label="시장 해석"
                value={marketState.metric}
                description={marketState.description}
              />
              <DeskMetric
                label="신뢰도"
                value={`${Math.round(data.confidence.score * 100)}%`}
                description={data.confidence.rationale}
              />
              <DeskMetric
                label="출처 상태"
                value={`${data.sourceSummary.sourceCount} / ${data.sourceSummary.missingDataCount}`}
                description="확인된 출처 수와 누락된 데이터 수입니다."
              />
            </div>

            <DataSourceNotice source={data.dataSource} className="mt-4 max-w-3xl" />
          </div>

          <div className="grid gap-3 xl:pl-2">
            <div className="rounded-md border border-border/80 bg-muted/10 p-4">
              <p className={typographyTokens.eyebrow}>오늘의 요약</p>
              <p className="mt-2 text-sm leading-7 text-foreground/88">
                {data.scenario}
              </p>
            </div>

            <div className="grid gap-2">
              <DeskActionLink
                href="/radar"
                icon={Radar}
                title="관심종목 좁히기"
                description="강한 섹터와 종목을 점수, 거래량, 이벤트로 비교합니다."
              />
              <DeskActionLink
                href="/news"
                icon={Newspaper}
                title="뉴스와 공시 보기"
                description="가격을 움직일 수 있는 기사와 국내 공시를 확인합니다."
              />
              <DeskActionLink
                href="/calendar"
                icon={CalendarDays}
                title="이벤트 일정 보기"
                description="실적 발표, 연준 일정, 공시 이벤트를 날짜로 정리합니다."
              />
              <DeskActionLink
                href="/history"
                icon={History}
                title="과거 반응 복기"
                description="비슷한 이벤트에서 가격이 어떻게 움직였는지 확인합니다."
              />
            </div>
          </div>
        </div>
      </section>

      <AiMarketSummaryCard data={data} />

      <IndexStrip items={data.indices} />

      <section className="grid gap-[var(--space-grid)] xl:grid-cols-[1.08fr_0.92fr]">
        <div className="grid gap-[var(--space-grid)]">
          <MarketHeatmap items={data.heatmap} />
          <SectorStrengthPanel items={data.sectors} />
        </div>
        <NewsPanel items={data.news} />
      </section>

      <RiskBanner
        risks={data.risks}
        confidence={data.confidence}
        sourceSummary={data.sourceSummary}
      />
    </div>
  );
}

function StatusPill({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  tone: Tone;
}) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-3 rounded-md border px-3 py-2 text-xs",
        tone === "positive"
          ? "border-[color:color-mix(in_oklch,var(--positive)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)]"
          : tone === "negative"
            ? "border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)]"
            : "border-border/80 bg-muted/15"
      )}
    >
      <span
        className={cn(
          "inline-flex size-7 items-center justify-center rounded-md border",
          tone === "positive"
            ? "border-[color:color-mix(in_oklch,var(--positive)_28%,transparent)] text-[color:var(--positive)]"
            : tone === "negative"
              ? "border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] text-[color:var(--negative)]"
              : "border-border/80 text-muted-foreground"
        )}
      >
        <Icon className="size-3.5" />
      </span>
      <div>
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <p className="mt-0.5 font-semibold tracking-normal text-foreground">
          {value}
        </p>
      </div>
    </div>
  );
}

function DeskMetric({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-md border border-border/80 bg-muted/10 p-4">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="numeric mt-2 text-lg font-semibold tracking-normal text-foreground">
        {value}
      </p>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
    </div>
  );
}

function DeskActionLink({
  href,
  icon: Icon,
  title,
  description,
}: {
  href: string;
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="group flex items-start justify-between gap-4 rounded-md border border-border/80 bg-card/70 px-4 py-4 transition hover:border-primary/35 hover:bg-card"
    >
      <div className="flex items-start gap-3">
        <span className="inline-flex size-9 items-center justify-center rounded-md border border-border/80 bg-muted/15 text-muted-foreground transition group-hover:border-primary/35 group-hover:text-primary">
          <Icon className="size-4" />
        </span>
        <div>
          <p className="text-sm font-semibold tracking-normal">{title}</p>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            {description}
          </p>
        </div>
      </div>
      <ArrowRight className="mt-0.5 size-4 shrink-0 text-muted-foreground transition group-hover:text-primary" />
    </Link>
  );
}

function getMarketState(data: OverviewFixture) {
  const positiveCount = data.indices.filter((item) => item.changePercent > 0).length;
  const negativeCount = data.indices.filter((item) => item.changePercent < 0).length;
  const leadScore = data.heatmap[0]?.score ?? 50;

  if (positiveCount >= negativeCount + 2 && leadScore >= 70) {
    return {
      label: "위험 선호",
      metric: "주도 섹터 우위",
      description: "강한 섹터가 시장 방향을 이끄는 구간입니다.",
      tone: "positive" as const,
    };
  }

  if (negativeCount > positiveCount) {
    return {
      label: "방어 우위",
      metric: "리스크 관리",
      description: "추격보다 지지선과 이벤트 확인이 먼저입니다.",
      tone: "negative" as const,
    };
  }

  return {
    label: "혼조",
    metric: "선별 필요",
    description: "시장 전체보다 강한 섹터와 종목을 따로 봐야 합니다.",
    tone: "neutral" as const,
  };
}

function getDataState(data: OverviewFixture) {
  if (data.dataSource.mode === "live") {
    return { label: "실제 데이터", tone: "positive" as const };
  }

  if (data.dataSource.mode === "fixture-fallback") {
    return { label: "목데이터", tone: "negative" as const };
  }

  if (data.dataSource.mode === "mock") {
    return { label: "목데이터", tone: "neutral" as const };
  }

  return { label: "목데이터", tone: "neutral" as const };
}
