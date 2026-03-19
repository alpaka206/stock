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
      title="시장 히트맵"
      description="강한 섹터와 약한 섹터를 한 번에 본다"
      action={
        <Link
          href="/radar"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
        >
          레이더 확장
        </Link>
      }
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className={cn(
              "rounded-[calc(var(--radius)*1.05)] border p-4 transition hover:-translate-y-0.5",
              getHeatTone(item.score)
            )}
          >
            <p className="text-sm font-semibold tracking-tight">{item.label}</p>
            <p className="numeric mt-4 text-3xl font-semibold">{item.score}</p>
            <p className="numeric mt-2 text-sm font-medium">
              {formatSignedPercent(item.changePercent)}
            </p>
            <p className="mt-3 text-xs font-semibold opacity-80">관련 종목 보기</p>
          </Link>
        ))}
      </div>
    </ResearchPanel>
  );
}

function getHeatTone(score: number) {
  if (score >= 80) {
    return "border-[color:color-mix(in_oklch,var(--positive)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_12%,transparent)] text-[color:var(--positive)]";
  }

  if (score <= 45) {
    return "border-[color:color-mix(in_oklch,var(--negative)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_12%,transparent)] text-[color:var(--negative)]";
  }

  return "border-border/60 bg-background/35 text-foreground";
}
