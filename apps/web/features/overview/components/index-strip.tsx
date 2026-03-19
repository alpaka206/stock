import Link from "next/link";

import { TrendChip } from "@/components/research/trend-chip";
import { formatPrice } from "@/lib/format";
import type { IndexStripItem, TrendDirection } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type IndexStripProps = {
  items: IndexStripItem[];
};

export function IndexStrip({ items }: IndexStripProps) {
  if (items.length === 0) {
    return (
      <section className="rounded-[calc(var(--radius)*1.3)] border border-border/60 bg-card/70 p-[var(--card-padding)]">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              시장 프록시
            </p>
            <h3 className="mt-1 text-base font-semibold tracking-tight">
              실시간 지수 스트립 데이터를 아직 받지 못했습니다
            </h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              요약과 뉴스는 live API를 사용 중이지만 지수 프록시 데이터는 응답에
              포함되지 않았습니다.
            </p>
          </div>
          <Link
            href="/history"
            className="inline-flex h-9 items-center justify-center rounded-[calc(var(--radius)*1.05)] border border-border/70 bg-background/70 px-4 text-sm font-semibold transition hover:bg-muted"
          >
            거시 흐름 보기
          </Link>
        </div>
      </section>
    );
  }

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
