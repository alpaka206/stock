import Link from "next/link";

import { TrendChip } from "@/components/research/trend-chip";
import { formatPrice } from "@/lib/format";
import type { IndexStripItem, TrendDirection } from "@/lib/research/types";
import { surfaceStyles, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type IndexStripProps = {
  items: IndexStripItem[];
};

export function IndexStrip({ items }: IndexStripProps) {
  if (items.length === 0) {
    return (
      <section className={cn(surfaceStyles.panel, "p-[var(--card-padding)]")}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className={typographyTokens.eyebrow}>핵심 지수 스트립</p>
            <h3 className="mt-1 text-base font-semibold tracking-tight">
              지수 스트립 데이터를 아직 받지 못했습니다
            </h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              헤드라인과 브리프는 내려왔지만 핵심 지수 데이터는 아직 응답에
              포함되지 않았습니다.
            </p>
          </div>
          <Link
            href="/history"
            className="inline-flex h-9 items-center justify-center rounded-[calc(var(--radius)*0.72)] border border-border/80 bg-muted/10 px-4 text-sm font-semibold transition hover:border-primary/35 hover:text-primary"
          >
            거시 흐름 보기
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className={cn(surfaceStyles.panel, "overflow-hidden")}>
      <div className="flex flex-col gap-3 border-b border-border/80 px-5 py-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className={typographyTokens.eyebrow}>핵심 지수 스트립</p>
          <h3 className="mt-1 text-base font-semibold tracking-tight">
            지수, 금리, 환율을 먼저 확인합니다
          </h3>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            전체 방향보다 무엇이 주도하고 무엇이 걸리는지 빠르게 스캔하는
            구간입니다.
          </p>
        </div>
        <Link
          href="/history"
          className="inline-flex h-9 items-center justify-center rounded-[calc(var(--radius)*0.72)] border border-border/80 bg-muted/10 px-4 text-sm font-semibold transition hover:border-primary/35 hover:text-primary"
        >
          과거 흐름 복기
        </Link>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-6">
        {items.map((item, index) => {
          const direction = getDirection(item.changePercent);
          const isLast = index === items.length - 1;

          return (
            <Link
              key={item.symbol}
              href={item.href}
              className={cn(
                "group flex min-h-[180px] flex-col justify-between px-5 py-4 transition hover:bg-muted/10",
                !isLast && "border-b border-border/80 xl:border-r xl:border-b-0"
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/80">
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
                <p className="numeric text-[1.55rem] font-semibold tracking-[-0.04em]">
                  {formatPrice(item.value)}
                </p>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  {item.note}
                </p>
              </div>
            </Link>
          );
        })}
      </div>
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
