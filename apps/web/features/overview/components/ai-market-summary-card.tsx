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
      eyebrow="Opening brief"
      title="시장 흐름 요약"
      description={`${data.asOf} 기준 서버 요약`}
      action={
        <Link
          href="/radar"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }), "rounded-md")}
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
            <p className={typographyTokens.eyebrow}>해석 프레임</p>
            <p className="mt-2 text-sm leading-7 text-foreground/88">
              {data.scenario}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <BriefMeta
              label="신뢰도"
              value={`${Math.round(data.confidence.score * 100)}%`}
              description={formatConfidenceLabel(data.confidence.label)}
            />
            <BriefMeta
              label="출처 수"
              value={`${data.sourceSummary.sourceCount}건`}
              description="요약에 반영된 서버 출처"
            />
            <BriefMeta
              label="누락 데이터"
              value={`${data.sourceSummary.missingDataCount}건`}
              description="응답에서 확인되지 않은 항목"
            />
          </div>
        </div>

        <div className="border-t border-border/80 pt-4 xl:border-l xl:border-t-0 xl:pl-6 xl:pt-0">
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
                          "mt-0.5 inline-flex size-9 items-center justify-center rounded-md border",
                          getDriverTone(driver.tone)
                        )}
                      >
                        <Icon className="size-4" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold tracking-normal">
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
            <div className="mt-3 rounded-md border border-dashed border-border/80 px-4 py-4 text-sm leading-6 text-muted-foreground">
              아직 판단 재료가 충분하지 않습니다. 레이더와 뉴스 화면에서 직접 확인하세요.
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
    <div className="rounded-md border border-border/80 bg-muted/10 px-4 py-3">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="numeric mt-2 text-lg font-semibold tracking-normal">{value}</p>
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

  return "보통";
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
