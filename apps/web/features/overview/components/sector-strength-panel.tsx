import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import { formatSignedPercent } from "@/lib/format";
import type { SectorStrengthItem } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type SectorStrengthPanelProps = {
  items: SectorStrengthItem[];
};

export function SectorStrengthPanel({ items }: SectorStrengthPanelProps) {
  return (
    <ResearchPanel
      eyebrow="Leader Tracking"
      title="리더 추적"
      description="상단 섹터의 점수, 모멘텀, 대표 종목을 한 줄씩 확인합니다."
      action={
        <Link
          href="/radar"
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "rounded-[calc(var(--radius)*0.72)]"
          )}
        >
          레이더 전체 보기
        </Link>
      }
      variant="feed"
    >
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-[calc(var(--radius)*0.82)] border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
            현재 추적할 상단 섹터가 없습니다. 레이더에서 섹터별 흐름을 직접 확인해 주세요.
          </div>
        ) : null}

        {items.length > 0 ? (
          <div className="divide-y divide-border/80">
            {items.map((item) => (
              <Link
                key={item.id}
                href={item.href}
                className="group block py-4 first:pt-0 last:pb-0"
              >
                <div className="grid gap-3 md:grid-cols-[1.1fr_0.9fr] md:items-start">
                  <div>
                    <div className="flex items-center gap-3">
                      <p className="text-sm font-semibold tracking-tight">{item.name}</p>
                      {item.changePercent !== undefined ? (
                        <span
                          className={cn(
                            "numeric text-xs font-semibold",
                            item.changePercent > 0
                              ? "tone-positive"
                              : item.changePercent < 0
                                ? "tone-negative"
                                : "tone-neutral"
                          )}
                        >
                          {formatSignedPercent(item.changePercent)}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">
                      {item.momentum}
                    </p>
                  </div>

                  <div className="md:text-right">
                    <p className="numeric text-[1.35rem] font-semibold tracking-[-0.04em]">
                      {item.score}
                    </p>
                    <p className="mt-1 text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/75">
                      {item.targetSymbol}
                    </p>
                    <p className="mt-2 text-xs leading-5 text-muted-foreground">
                      {item.catalysts.slice(0, 2).join(" · ")}
                    </p>
                    <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary md:justify-end">
                      {item.href === "/radar" ? "레이더 보기" : `${item.targetSymbol} 보기`}
                      <ArrowRight className="size-3.5" />
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : null}
      </div>
    </ResearchPanel>
  );
}
