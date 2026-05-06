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
      eyebrow="Sector Flow"
      title="섹터 플로우"
      description="강한 섹터와 밀리는 섹터를 같은 눈금으로 비교합니다."
      action={
        <Link
          href="/radar"
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "rounded-[calc(var(--radius)*0.72)]"
          )}
        >
          레이더 확장
        </Link>
      }
    >
      {items.length === 0 ? (
        <div className="rounded-[calc(var(--radius)*0.82)] border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
          현재 비교할 섹터 흐름 데이터가 없습니다. 레이더와 뉴스에서 상단 흐름을
          직접 확인해 주세요.
        </div>
      ) : null}

      {items.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-[calc(var(--radius)*0.82)] border border-border/80 bg-border/80 sm:grid-cols-3">
            {items.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex min-h-[128px] flex-col justify-between bg-card px-4 py-4 transition hover:bg-muted/15",
                  getHeatTone(item.score)
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">{item.label}</p>
                  {item.changePercent !== undefined ? (
                    <p className="numeric text-xs font-semibold">
                      {formatSignedPercent(item.changePercent)}
                    </p>
                  ) : null}
                </div>

                <div>
                  <p className="numeric text-[1.45rem] font-semibold tracking-[-0.04em]">
                    {item.score}
                  </p>
                  <p className="mt-1 text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/75">
                    score
                  </p>
                </div>
              </Link>
            ))}
          </div>

          <div className="grid gap-2 text-[0.72rem] text-muted-foreground sm:grid-cols-3">
            <div className="rounded-[0.42rem] border border-border/80 bg-muted/10 px-3 py-2">
              75 이상: 상단 주도 흐름
            </div>
            <div className="rounded-[0.42rem] border border-border/80 bg-muted/10 px-3 py-2">
              50 전후: 중립 구간
            </div>
            <div className="rounded-[0.42rem] border border-border/80 bg-muted/10 px-3 py-2">
              45 이하: 약세 또는 후순위
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
