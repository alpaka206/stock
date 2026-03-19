import Link from "next/link";

import { AiMarketSummaryCard } from "@/features/overview/components/ai-market-summary-card";
import { IndexStrip } from "@/features/overview/components/index-strip";
import { MarketHeatmap } from "@/features/overview/components/market-heatmap";
import { NewsPanel } from "@/features/overview/components/news-panel";
import { RiskBanner } from "@/features/overview/components/risk-banner";
import { SectorStrengthPanel } from "@/features/overview/components/sector-strength-panel";
import type { OverviewFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";

type OverviewPageProps = {
  data: OverviewFixture;
};

export function OverviewPage({ data }: OverviewPageProps) {
  return (
    <div className={layoutTokens.page}>
      <section className="flex flex-col gap-4 rounded-[calc(var(--radius)*1.5)] border border-border/60 bg-[radial-gradient(circle_at_top_left,color-mix(in_oklch,var(--primary)_12%,transparent),transparent_50%),linear-gradient(180deg,color-mix(in_oklch,var(--background)_88%,var(--card))_0%,var(--background)_100%)] p-[var(--card-padding)] lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <p className={typographyTokens.eyebrow}>오늘 시장 한눈에</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight lg:text-3xl">
            10초 안에 읽는 오늘의 시장 방향
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground lg:text-base">
            지수 스트립으로 온도를 먼저 보고, AI 시황 요약과 히트맵으로
            주도 섹터를 확인한 뒤 뉴스와 리스크로 다음 화면 이동 경로를
            정합니다.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link
            href="/radar"
            className="inline-flex h-9 items-center justify-center rounded-[calc(var(--radius)*1.05)] bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
          >
            레이더 열기
          </Link>
          <Link
            href="/history"
            className="inline-flex h-9 items-center justify-center rounded-[calc(var(--radius)*1.05)] border border-border/70 bg-background/70 px-4 text-sm font-semibold transition hover:bg-muted"
          >
            과거 반응 보기
          </Link>
        </div>
      </section>

      <IndexStrip items={data.indices} />

      <section className={layoutTokens.heroGrid}>
        <AiMarketSummaryCard data={data} />
        <MarketHeatmap items={data.heatmap} />
      </section>

      <section className="grid gap-[var(--space-grid)] xl:grid-cols-[1.15fr_0.85fr]">
        <NewsPanel items={data.news} />
        <SectorStrengthPanel items={data.sectors} />
      </section>

      <RiskBanner
        risks={data.risks}
        confidence={data.confidence}
        sourceSummary={data.sourceSummary}
      />
    </div>
  );
}
