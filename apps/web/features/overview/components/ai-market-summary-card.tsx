import Link from "next/link";
import { ArrowRight, ShieldAlert, Sparkles, Telescope } from "lucide-react";

import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import { surfaceStyles, typographyTokens } from "@/lib/tokens";
import type { OverviewFixture, Tone } from "@/lib/research/types";
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
      eyebrow="Opening Brief"
      title="오프닝 브리프"
      description={`${data.asOf} 기준 시장 해석`}
      action={
        <Link
          href="/radar"
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "rounded-[calc(var(--radius)*0.72)]"
          )}
        >
          레이더로 이어서 보기
        </Link>
      }
      className="overflow-hidden"
      variant="brief"
    >
      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="min-w-0 space-y-4">
          <p className="text-[1.02rem] leading-8 text-foreground/90 lg:text-[1.08rem]">
            {data.lead}
          </p>

          <div className={cn(surfaceStyles.panelInset, "p-4")}>
            <p className={typographyTokens.eyebrow}>오늘의 해석 프레임</p>
            <p className="mt-2 text-sm leading-7 text-foreground/88">
              {data.scenario}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <BriefMeta
              label="판단 신뢰도"
              value={`${Math.round(data.confidence.score * 100)}점`}
              description={formatConfidenceLabel(data.confidence.label)}
            />
            <BriefMeta
              label="출처 수"
              value={`${data.sourceSummary.sourceCount}건`}
              description="브리프에 반영된 데이터 출처"
            />
            <BriefMeta
              label="데이터 공백"
              value={`${data.sourceSummary.missingDataCount}건`}
              description="현재 응답에서 누락된 항목"
            />
          </div>

          <div className="rounded-[calc(var(--radius)*0.82)] border border-border/80 bg-muted/10 px-4 py-3 text-sm leading-6 text-muted-foreground">
            {data.confidence.rationale}
          </div>
        </div>

        <div className="border-t border-border/80 pt-4 xl:border-t-0 xl:border-l xl:pl-6 xl:pt-0">
          <p className={typographyTokens.eyebrow}>판단 재료</p>
          {data.summaryDrivers.length > 0 ? (
            <div className="mt-3 divide-y divide-border/80">
              {data.summaryDrivers.map((driver) => {
                const Icon = driverIconMap[driver.tone];

                return (
                  <Link
                    key={driver.label}
                    href={driver.href}
                    className="group block py-4 first:pt-0 last:pb-0"
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={cn(
                          "mt-0.5 inline-flex size-9 items-center justify-center rounded-[0.5rem] border",
                          getDriverTone(driver.tone)
                        )}
                      >
                        <Icon className="size-4" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold tracking-tight">
                            {driver.label}
                          </p>
                          <ArrowRight className="size-4 shrink-0 text-muted-foreground transition group-hover:text-primary" />
                        </div>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                          {driver.text}
                        </p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="mt-3 rounded-[calc(var(--radius)*0.82)] border border-dashed border-border/80 px-4 py-4 text-sm leading-6 text-muted-foreground">
              브리프를 구성할 판단 재료가 아직 충분하지 않습니다. 레이더와
              히스토리에서 직접 흐름을 확인해 주세요.
            </div>
          )}
        </div>
      </div>
    </ResearchPanel>
  );
}

function BriefMeta({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-[calc(var(--radius)*0.8)] border border-border/80 bg-muted/10 px-4 py-3">
      <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/80">
        {label}
      </p>
      <p className="numeric mt-2 text-lg font-semibold tracking-tight">{value}</p>
      <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
        {description}
      </p>
    </div>
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

  return "border-border/70 bg-muted/15 text-muted-foreground";
}
