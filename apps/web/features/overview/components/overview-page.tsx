import Link from "next/link";
import {
  Activity,
  ArrowRight,
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
        <div className="grid gap-6 xl:grid-cols-[1.18fr_0.82fr]">
          <div className="min-w-0">
            <div className="flex flex-wrap gap-2">
              <StatusPill
                icon={Activity}
                label="장 상태"
                value={marketState.label}
                tone={marketState.tone}
              />
              <StatusPill
                icon={Clock3}
                label="최종 업데이트"
                value={data.asOf}
                tone="neutral"
              />
              <StatusPill
                icon={Database}
                label="데이터 상태"
                value={dataState.label}
                tone={dataState.tone}
              />
            </div>

            <div className="mt-5 max-w-4xl">
              <p className={typographyTokens.eyebrow}>시장 판단 시작점</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-[-0.04em] lg:text-[2rem]">
                오늘 시장을 어디서부터 읽을지 먼저 정리합니다
              </h2>
              <p className="mt-3 text-sm leading-7 text-muted-foreground lg:text-[0.96rem]">
                장 상태와 데이터 지연 여부를 확인한 뒤, 오프닝 브리프에서
                해석을 잡고 지수 스트립, 섹터 플로우, 헤드라인 플로우,
                오늘의 리스크 체크 순서로 내려갑니다.
              </p>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-3">
              <DeskMetric
                label="시장 톤"
                value={marketState.metric}
                description={marketState.description}
              />
              <DeskMetric
                label="판단 신뢰도"
                value={`${Math.round(data.confidence.score * 100)}점`}
                description={data.confidence.rationale}
              />
              <DeskMetric
                label="데이터 커버리지"
                value={`${data.sourceSummary.sourceCount} / ${data.sourceSummary.missingDataCount}`}
                description="출처 수 / 누락 데이터 수를 함께 봅니다."
              />
            </div>

            <DataSourceNotice source={data.dataSource} className="mt-4 max-w-3xl" />
          </div>

          <div className="grid gap-3 xl:pl-2">
            <div className="rounded-[calc(var(--radius)*0.9)] border border-border/80 bg-muted/10 p-4">
              <p className={typographyTokens.eyebrow}>오늘 시장 메모</p>
              <p className="mt-2 text-sm leading-7 text-foreground/88">
                {data.scenario}
              </p>
            </div>

            <div className="grid gap-2">
              <DeskActionLink
                href="/radar"
                icon={Radar}
                title="레이더 열기"
                description="상단 섹터와 관심 종목을 바로 비교합니다."
              />
              <DeskActionLink
                href="/news"
                icon={Newspaper}
                title="헤드라인 전체 보기"
                description="흐름을 바꿀 수 있는 기사만 이어서 읽습니다."
              />
              <DeskActionLink
                href="/history"
                icon={History}
                title="과거 반응 복기"
                description="이벤트와 급등락 반응을 과거 차트로 다시 읽습니다."
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
        "inline-flex items-center gap-3 rounded-[0.5rem] border px-3 py-2 text-xs",
        tone === "positive"
          ? "border-[color:color-mix(in_oklch,var(--positive)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)]"
          : tone === "negative"
            ? "border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)]"
            : "border-border/80 bg-muted/15"
      )}
    >
      <span
        className={cn(
          "inline-flex size-7 items-center justify-center rounded-[0.45rem] border",
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
        <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/80">
          {label}
        </p>
        <p className="mt-0.5 font-semibold tracking-tight text-foreground">
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
    <div className="rounded-[calc(var(--radius)*0.82)] border border-border/80 bg-muted/10 p-4">
      <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/80">
        {label}
      </p>
      <p className="numeric mt-2 text-lg font-semibold tracking-tight text-foreground">
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
      className="group flex items-start justify-between gap-4 rounded-[calc(var(--radius)*0.82)] border border-border/80 bg-card/70 px-4 py-4 transition hover:border-primary/35 hover:bg-card"
    >
      <div className="flex items-start gap-3">
        <span className="inline-flex size-9 items-center justify-center rounded-[0.5rem] border border-border/80 bg-muted/15 text-muted-foreground transition group-hover:border-primary/35 group-hover:text-primary">
          <Icon className="size-4" />
        </span>
        <div>
          <p className="text-sm font-semibold tracking-tight">{title}</p>
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
      label: "리스크 온",
      metric: "상단 테마 주도",
      description: "주도 섹터가 시장 상승 폭을 끌고 가는 장세입니다.",
      tone: "positive" as const,
    };
  }

  if (negativeCount > positiveCount) {
    return {
      label: "방어 우위",
      metric: "리스크 관리 우선",
      description: "지수보다 방어적 해석과 손절 기준 점검이 먼저 필요한 구간입니다.",
      tone: "negative" as const,
    };
  }

  return {
    label: "혼조",
    metric: "선별 대응",
    description: "전체 시장보다 상단 리더와 헤드라인 변화를 좁혀서 볼 구간입니다.",
    tone: "neutral" as const,
  };
}

function getDataState(data: OverviewFixture) {
  if (data.dataSource.mode === "live") {
    return { label: "실시간", tone: "positive" as const };
  }

  if (data.dataSource.mode === "fixture-fallback") {
    return { label: "대체 데이터", tone: "negative" as const };
  }

  if (data.dataSource.mode === "mock") {
    return { label: "모의 데이터", tone: "neutral" as const };
  }

  return { label: "기본 데이터", tone: "neutral" as const };
}
