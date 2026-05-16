import { ArrowRight } from "lucide-react";
import Link from "next/link";

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
      eyebrow="Leader tracking"
      title="주도 섹터"
      description="점수, 모멘텀, 대표 종목을 기준으로 시장 리더를 봅니다."
      action={
        <Link href="/radar" className={buttonVariants({ variant: "outline", size: "sm" })}>
          레이더 전체
        </Link>
      }
      variant="feed"
    >
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
            추적할 주도 섹터가 없습니다. 레이더에서 섹터별 흐름을 확인해 주세요.
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
                      <p className="text-sm font-semibold">{item.name}</p>
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
                    <p className="numeric text-2xl font-semibold">{item.score}</p>
                    <p className="mt-1 text-[0.72rem] font-semibold uppercase text-muted-foreground/75">
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
