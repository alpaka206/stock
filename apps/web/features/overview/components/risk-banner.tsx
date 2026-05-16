import { AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";
import Link from "next/link";

import { ResearchPanel } from "@/components/research/research-panel";
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
  const primaryRisk = risks[0] ?? {
    label: "확인할 위험 데이터가 부족합니다.",
    value: "대기",
    detail:
      "리스크 판단에 필요한 가격, 뉴스, 공시 데이터가 충분하지 않습니다. 먼저 데이터 출처 연결 상태를 확인해 주세요.",
    tone: "neutral" as Tone,
    href: "/history",
  };
  const riskItems = risks.length > 0 ? risks : [primaryRisk];

  return (
    <ResearchPanel
      eyebrow="Risk check"
      title="오늘의 위험 체크"
      description="강세 근거보다 먼저 깨질 수 있는 조건과 데이터 공백을 확인합니다."
      action={
        <Link href="/history" className={buttonVariants({ variant: "outline", size: "sm" })}>
          히스토리 보기
        </Link>
      }
      className="bg-[linear-gradient(180deg,color-mix(in_oklch,var(--negative)_5%,var(--card)),var(--card))]"
      variant="risk"
    >
      <div className="grid gap-6 xl:grid-cols-[0.82fr_1.18fr]">
        <div className="border-b border-border/80 pb-4 xl:border-r xl:border-b-0 xl:pr-6 xl:pb-0">
          <div className="flex items-center gap-3">
            <span className="inline-flex size-10 items-center justify-center rounded-lg border border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)] text-[color:var(--negative)]">
              <AlertTriangle className="size-4.5" />
            </span>
            <div>
              <p className="text-[0.68rem] font-semibold uppercase text-muted-foreground/80">
                먼저 확인
              </p>
              <p className="mt-1 text-sm font-semibold">{primaryRisk.value}</p>
            </div>
          </div>

          <p className="mt-4 text-lg font-semibold">{primaryRisk.label}</p>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            {primaryRisk.detail}
          </p>

          <div className="mt-5 grid gap-px overflow-hidden rounded-lg border border-border/80 bg-border/80 sm:grid-cols-3">
            <RiskMeta label="판단 신뢰도" value={formatConfidenceLabel(confidence.label)} />
            <RiskMeta label="출처 수" value={`${sourceSummary.sourceCount}건`} />
            <RiskMeta label="누락 데이터" value={`${sourceSummary.missingDataCount}건`} />
          </div>
        </div>

        <div className="divide-y divide-border/80">
          {riskItems.map((risk, index) => (
            <Link
              key={`${risk.label}-${risk.value}`}
              href={risk.href}
              className="group block py-4 first:pt-0 last:pb-0"
            >
              <div className="grid gap-3 md:grid-cols-[80px_minmax(0,1fr)_96px] md:items-start">
                <div className="flex items-center gap-2 text-[0.72rem] font-semibold uppercase text-muted-foreground/80">
                  <ShieldCheck className={cn("size-4", getRiskToneText(risk.tone))} />
                  <span className="numeric">{String(index + 1).padStart(2, "0")}</span>
                </div>

                <div>
                  <p className="text-sm font-semibold">{risk.label}</p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {risk.detail}
                  </p>
                </div>

                <div className="flex items-center justify-between gap-3 md:block md:text-right">
                  <p className="numeric text-sm font-semibold text-foreground">
                    {risk.value}
                  </p>
                  <p className="mt-0 text-xs font-semibold text-primary md:mt-3">
                    확인
                    <ArrowRight className="ml-1 inline size-3.5 align-middle" />
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </ResearchPanel>
  );
}

function RiskMeta({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-card px-4 py-3">
      <p className="text-[0.68rem] font-semibold uppercase text-muted-foreground/80">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-foreground">{value}</p>
    </div>
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

function getRiskToneText(tone: Tone) {
  if (tone === "positive") {
    return "text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "text-[color:var(--negative)]";
  }

  return "text-muted-foreground";
}
