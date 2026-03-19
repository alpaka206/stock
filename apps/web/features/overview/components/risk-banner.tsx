import Link from "next/link";
import { AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";

import { ResearchPanel } from "@/components/research/research-panel";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import type {
  OverviewConfidence,
  OverviewSourceSummary,
  RiskBannerItem,
  Tone,
} from "@/lib/research/types";
import { cn } from "@/lib/utils";

type RiskBannerProps = {
  risks: RiskBannerItem[];
  confidence: OverviewConfidence;
  sourceSummary: OverviewSourceSummary;
};

export function RiskBanner({
  risks,
  confidence,
  sourceSummary,
}: RiskBannerProps) {
  const primaryRisk = risks[0];

  return (
    <ResearchPanel
      title="리스크 배너"
      description="포지션 확대 전에 체크할 경계선을 먼저 본다"
      action={
        <Link
          href="/history"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
        >
          히스토리로 이동
        </Link>
      }
      className="border-[color:color-mix(in_oklch,var(--negative)_18%,var(--border))] bg-[linear-gradient(180deg,color-mix(in_oklch,var(--negative)_7%,transparent),transparent_45%)]"
    >
      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-[calc(var(--radius)*1.15)] border border-border/60 bg-background/45 p-5">
          <div className="flex items-center gap-2">
            <span className="inline-flex size-10 items-center justify-center rounded-full border border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)] text-[color:var(--negative)]">
              <AlertTriangle className="size-4.5" />
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight">
                오늘 가장 먼저 볼 리스크
              </p>
              <p className="text-xs text-muted-foreground">{primaryRisk.value}</p>
            </div>
          </div>

          <p className="mt-4 text-base font-semibold tracking-tight">
            {primaryRisk.label}
          </p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {primaryRisk.detail}
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <Badge
              variant="outline"
              className="rounded-full border-border/70 bg-background/55 px-3 py-1 text-xs"
            >
              신뢰도 {formatConfidenceLabel(confidence.label)}
            </Badge>
            <Badge
              variant="outline"
              className="rounded-full border-border/70 bg-background/55 px-3 py-1 text-xs"
            >
              출처 {sourceSummary.sourceCount}건
            </Badge>
            <Badge
              variant="outline"
              className="rounded-full border-border/70 bg-background/55 px-3 py-1 text-xs"
            >
              누락 {sourceSummary.missingDataCount}건
            </Badge>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          {risks.map((risk) => (
            <Link
              key={`${risk.label}-${risk.value}`}
              href={risk.href}
              className="rounded-[calc(var(--radius)*1.05)] border border-border/60 bg-background/35 p-4 transition hover:border-primary/30 hover:bg-background/55"
            >
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "inline-flex size-8 items-center justify-center rounded-full border",
                    getRiskTone(risk.tone)
                  )}
                >
                  <ShieldCheck className="size-4" />
                </span>
                <div>
                  <p className="text-sm font-semibold tracking-tight">{risk.label}</p>
                  <p className="text-xs text-muted-foreground">{risk.value}</p>
                </div>
              </div>

              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                {risk.detail}
              </p>

              <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary">
                관련 맥락 보기
                <ArrowRight className="size-3.5" />
              </p>
            </Link>
          ))}
        </div>
      </div>
    </ResearchPanel>
  );
}

function formatConfidenceLabel(label: OverviewConfidence["label"]) {
  if (label === "high") {
    return "높음";
  }

  if (label === "low") {
    return "낮음";
  }

  return "중간";
}

function getRiskTone(tone: Tone) {
  if (tone === "positive") {
    return "border-[color:color-mix(in_oklch,var(--positive)_30%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_12%,transparent)] text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "border-[color:color-mix(in_oklch,var(--negative)_30%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_12%,transparent)] text-[color:var(--negative)]";
  }

  return "border-border/70 bg-background/70 text-muted-foreground";
}
