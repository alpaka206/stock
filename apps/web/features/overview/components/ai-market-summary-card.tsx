import Link from "next/link";
import { ArrowRight, ShieldAlert, Sparkles, Telescope } from "lucide-react";

import { ResearchPanel } from "@/components/research/research-panel";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import type { OverviewFixture, Tone } from "@/lib/research/types";
import { typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type AiMarketSummaryCardProps = {
  data: OverviewFixture;
};

const driverIconMap = {
  positive: Sparkles,
  neutral: Telescope,
  negative: ShieldAlert,
} as const;

export function AiMarketSummaryCard({ data }: AiMarketSummaryCardProps) {
  return (
    <ResearchPanel
      title="AI 시황 요약 카드"
      description={`${data.asOf} 기준`}
      action={
        <Link
          href="/radar"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
        >
          레이더로 이동
        </Link>
      }
      className="overflow-hidden"
    >
      <div className="space-y-5">
        <div className="space-y-3">
          <p className="text-base leading-7 text-foreground/90 lg:text-lg">
            {data.lead}
          </p>
          <div className="rounded-[calc(var(--radius)*1.1)] border border-border/60 bg-background/40 p-4">
            <p className={typographyTokens.eyebrow}>오늘의 관전 포인트</p>
            <p className="mt-2 text-sm leading-6 text-foreground/85">
              {data.scenario}
            </p>
          </div>
        </div>

        {data.summaryDrivers.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-3">
            {data.summaryDrivers.map((driver) => {
              const Icon = driverIconMap[driver.tone];

              return (
                <Link
                  key={driver.label}
                  href={driver.href}
                  className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4 transition hover:border-primary/30 hover:bg-background/45"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "inline-flex size-8 items-center justify-center rounded-full border",
                        getDriverTone(driver.tone)
                      )}
                    >
                      <Icon className="size-4" />
                    </span>
                    <p className="text-sm font-semibold tracking-tight">{driver.label}</p>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted-foreground">
                    {driver.text}
                  </p>
                  <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary">
                    자세히 보기
                    <ArrowRight className="size-3.5" />
                  </p>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="rounded-[calc(var(--radius)*1.05)] border border-dashed border-border/70 bg-background/20 p-4 text-sm leading-6 text-muted-foreground">
            현재 요약 신호 카드가 충분하지 않습니다. 출처 수와 누락 데이터를 확인한 뒤 레이더와 히스토리 화면으로 이동해 주세요.
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <Badge
            variant="outline"
            className="rounded-full border-border/70 bg-background/50 px-3 py-1 text-xs"
          >
            신뢰도 {formatConfidenceLabel(data.confidence.label)} ·{" "}
            {Math.round(data.confidence.score * 100)}점
          </Badge>
          <Badge
            variant="outline"
            className="rounded-full border-border/70 bg-background/50 px-3 py-1 text-xs"
          >
            출처 {data.sourceSummary.sourceCount}건
          </Badge>
          <Badge
            variant="outline"
            className="rounded-full border-border/70 bg-background/50 px-3 py-1 text-xs"
          >
            누락 데이터 {data.sourceSummary.missingDataCount}건
          </Badge>
        </div>
      </div>
    </ResearchPanel>
  );
}

function formatConfidenceLabel(label: OverviewFixture["confidence"]["label"]) {
  if (label === "high") {
    return "높음";
  }

  if (label === "low") {
    return "낮음";
  }

  return "중간";
}

function getDriverTone(tone: Tone) {
  if (tone === "positive") {
    return "border-[color:color-mix(in_oklch,var(--positive)_30%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_12%,transparent)] text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "border-[color:color-mix(in_oklch,var(--negative)_30%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_12%,transparent)] text-[color:var(--negative)]";
  }

  return "border-border/70 bg-background/70 text-muted-foreground";
}
