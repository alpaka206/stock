import Link from "next/link";

import { TrendChip } from "@/components/research/trend-chip";
import { formatPrice } from "@/lib/format";
import type { IndexStripItem, TrendDirection } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type IndexStripProps = {
  items: IndexStripItem[];
};

export function IndexStrip({ items }: IndexStripProps) {
  return (
    <section className="grid gap-[var(--space-grid)] md:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => {
        const direction = getDirection(item.changePercent);

        return (
          <Link
            key={item.symbol}
            href={item.href}
            className={cn(
              "group rounded-[calc(var(--radius)*1.3)] border border-border/60 bg-card/85 p-[var(--card-padding)] transition hover:-translate-y-0.5 hover:border-primary/35 hover:bg-card"
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  {item.category}
                </p>
                <h3 className="mt-1 text-base font-semibold tracking-tight">
                  {item.name}
                </h3>
                <p className="mt-1 text-xs text-muted-foreground">{item.symbol}</p>
              </div>
              <TrendChip direction={direction} value={item.changePercent} />
            </div>

            <div className="mt-5">
              <p className="numeric text-2xl font-semibold tracking-tight">
                {formatPrice(item.value)}
              </p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {item.note}
              </p>
            </div>

            <p className="mt-4 text-xs font-semibold text-primary">
              관련 흐름 보기
            </p>
          </Link>
        );
      })}
    </section>
  );
}

function getDirection(value: number): TrendDirection {
  if (value > 0.05) {
    return "up";
  }

  if (value < -0.05) {
    return "down";
  }

  return "flat";
}
