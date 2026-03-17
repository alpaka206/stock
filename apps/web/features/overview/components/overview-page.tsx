import { ResearchPanel } from "@/components/research/research-panel";
import { TrendChip } from "@/components/research/trend-chip";
import { SectorSummaryPanel } from "@/features/sector/components/sector-summary-panel";
import { formatPrice } from "@/lib/format";
import type { OverviewFixture, Tone, TrendDirection } from "@/lib/research/types";
import { layoutTokens, surfaceStyles, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type OverviewPageProps = {
  data: OverviewFixture;
};

export function OverviewPage({ data }: OverviewPageProps) {
  return (
    <div className={layoutTokens.page}>
      <section className="grid gap-[var(--space-grid)] xl:grid-cols-4">
        {data.indices.map((indexItem) => {
          const direction = getDirection(indexItem.changePercent);

          return (
            <div
              key={indexItem.symbol}
              className={cn(
                surfaceStyles.panel,
                "space-y-3 p-[var(--card-padding)]"
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className={typographyTokens.eyebrow}>{indexItem.symbol}</p>
                  <h2 className="text-base font-semibold tracking-tight">
                    {indexItem.name}
                  </h2>
                </div>
                <TrendChip direction={direction} value={indexItem.changePercent} />
              </div>
              <div>
                <p className="numeric text-2xl font-semibold tracking-tight">
                  {formatPrice(indexItem.value)}
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                  {indexItem.note}
                </p>
              </div>
            </div>
          );
        })}
      </section>

      <section className={layoutTokens.heroGrid}>
        <ResearchPanel
          title="AI 시황 요약"
          description={`기준 시각 ${data.asOf}`}
        >
          <div className="space-y-4">
            <p className={typographyTokens.body}>{data.lead}</p>
            <div className="rounded-[calc(var(--radius)*1.1)] border border-border/55 bg-background/35 p-4">
              <p className={typographyTokens.eyebrow}>오늘의 관전 포인트</p>
              <p className="mt-2 text-sm leading-6 text-foreground/85">
                {data.scenario}
              </p>
            </div>
          </div>
        </ResearchPanel>

        <ResearchPanel title="시장 히트맵" description="섹터 강도와 하루 변화율">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {data.heatmap.map((tile) => (
              <div
                key={tile.label}
                className={cn(
                  "rounded-[calc(var(--radius)*1.05)] border p-3",
                  getHeatTone(tile.score)
                )}
              >
                <p className="text-sm font-semibold tracking-tight">
                  {tile.label}
                </p>
                <p className="numeric mt-3 text-2xl font-semibold">
                  {tile.score}
                </p>
                <p className="numeric mt-1 text-xs font-medium">
                  {tile.changePercent > 0 ? "+" : ""}
                  {tile.changePercent.toFixed(2)}%
                </p>
              </div>
            ))}
          </div>
        </ResearchPanel>
      </section>

      <section className="grid gap-[var(--space-grid)] xl:grid-cols-[1.15fr_0.85fr]">
        <ResearchPanel title="뉴스 흐름" description="리서치 시작 전에 읽을 핵심 문맥">
          <div className="space-y-3">
            {data.news.map((newsItem) => (
              <article
                key={newsItem.id}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">
                    {newsItem.headline}
                  </p>
                  <span
                    className={cn(
                      "rounded-full px-2 py-1 text-[0.68rem] font-semibold",
                      getToneBadge(newsItem.tone)
                    )}
                  >
                    {newsItem.impactLabel}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {newsItem.summary}
                </p>
                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{newsItem.source}</span>
                  <span className="numeric">{newsItem.publishedAt}</span>
                </div>
              </article>
            ))}
          </div>
        </ResearchPanel>

        <SectorSummaryPanel
          title="섹터 강도"
          description="강한 섹터와 약한 섹터를 한 흐름으로 본다"
          items={data.sectors.map((sector) => ({
            label: sector.name,
            score: sector.score,
            summary: sector.momentum,
            meta: sector.catalysts[0],
            changePercent: sector.changePercent,
          }))}
        />
      </section>

      <section className={layoutTokens.denseGrid}>
        {data.risks.map((risk) => (
          <ResearchPanel
            key={risk.label}
            title={risk.label}
            description={risk.value}
            size="sm"
          >
            <p className={typographyTokens.body}>{risk.detail}</p>
            <p
              className={cn(
                "mt-3 text-xs font-semibold uppercase tracking-[0.16em]",
                risk.tone === "positive"
                  ? "tone-positive"
                  : risk.tone === "negative"
                    ? "tone-negative"
                    : "tone-neutral"
              )}
            >
              {risk.tone === "positive"
                ? "리스크 완화"
                : risk.tone === "negative"
                  ? "리스크 확대"
                  : "중립 점검"}
            </p>
          </ResearchPanel>
        ))}
      </section>
    </div>
  );
}

function getDirection(value: number): TrendDirection {
  if (value > 0.05) {
    return "up";
  }

  if (value < -0.05) {
    return "down";
  }

  return "flat";
}

function getHeatTone(score: number) {
  if (score >= 80) {
    return "border-[color:color-mix(in_oklch,var(--positive)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_12%,transparent)] text-[color:var(--positive)]";
  }

  if (score <= 45) {
    return "border-[color:color-mix(in_oklch,var(--negative)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_12%,transparent)] text-[color:var(--negative)]";
  }

  return "border-border/60 bg-background/35 text-foreground";
}

function getToneBadge(tone: Tone) {
  if (tone === "positive") {
    return "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]";
  }

  return "bg-muted text-muted-foreground";
}
