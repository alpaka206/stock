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
      title="섹터 강도 패널"
      description="강한 섹터에서 바로 종목 분석으로 이동한다"
      action={
        <Link
          href="/radar"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
        >
          레이더 전체 보기
        </Link>
      }
    >
      <div className="space-y-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="block rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4 transition hover:border-primary/30 hover:bg-background/45"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
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

              <div className="text-right">
                <p className="numeric text-xl font-semibold">{item.score}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {item.targetSymbol}
                </p>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {item.catalysts.slice(0, 2).map((catalyst) => (
                <span
                  key={catalyst}
                  className="rounded-full border border-border/60 bg-background/55 px-2.5 py-1 text-[0.68rem] font-medium text-muted-foreground"
                >
                  {catalyst}
                </span>
              ))}
            </div>

            <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary">
              {item.href === "/radar" ? "레이더에서 보기" : `${item.targetSymbol} 분석 보기`}
              <ArrowRight className="size-3.5" />
            </p>
          </Link>
        ))}
      </div>
    </ResearchPanel>
  );
}
