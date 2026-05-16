import Link from "next/link";

import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import { formatSignedPercent } from "@/lib/format";
import type { HeatmapTile } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type MarketHeatmapProps = {
  items: HeatmapTile[];
};

export function MarketHeatmap({ items }: MarketHeatmapProps) {
  return (
    <ResearchPanel
      eyebrow="Sector flow"
      title="섹터 흐름"
      description="강한 섹터와 식어가는 섹터를 같은 기준으로 비교합니다."
      action={
        <Link href="/radar" className={buttonVariants({ variant: "outline", size: "sm" })}>
          레이더 열기
        </Link>
      }
    >
      {items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
          비교할 섹터 데이터가 없습니다. 레이더나 뉴스 화면에서 원자료를 확인해 주세요.
        </div>
      ) : null}

      {items.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border/80 bg-border/80 sm:grid-cols-3">
            {items.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex min-h-[128px] flex-col justify-between bg-card px-4 py-4 transition hover:bg-muted/25",
                  getHeatTone(item.score)
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold">{item.label}</p>
                  {item.changePercent !== undefined ? (
                    <p className="numeric text-xs font-semibold">
                      {formatSignedPercent(item.changePercent)}
                    </p>
                  ) : null}
                </div>

                <div>
                  <p className="numeric text-2xl font-semibold">{item.score}</p>
                  <p className="mt-1 text-[0.72rem] font-semibold uppercase text-muted-foreground/75">
                    score
                  </p>
                </div>
              </Link>
            ))}
          </div>

          <div className="grid gap-2 text-[0.72rem] text-muted-foreground sm:grid-cols-3">
            <div className="rounded-md border border-border/80 bg-muted/10 px-3 py-2">
              75 이상: 주도 흐름
            </div>
            <div className="rounded-md border border-border/80 bg-muted/10 px-3 py-2">
              50 전후: 중립 구간
            </div>
            <div className="rounded-md border border-border/80 bg-muted/10 px-3 py-2">
              45 이하: 약세 또는 관망
            </div>
          </div>
        </div>
      ) : null}
    </ResearchPanel>
  );
}

function getHeatTone(score: number) {
  if (score >= 80) {
    return "text-[color:var(--positive)]";
  }

  if (score <= 45) {
    return "text-[color:var(--negative)]";
  }

  return "text-foreground";
}
