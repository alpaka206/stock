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
        <p className={typographyTokens.eyebrow}>핵심 지표</p>
        <h3 className="mt-1 text-base font-semibold tracking-normal">
          아직 지표 데이터를 받지 못했습니다.
        </h3>
      </section>
    );
  }

  return (
    <section className={cn(surfaceStyles.panel, "overflow-hidden")}>
      <div className="flex flex-col gap-3 border-b border-border/80 px-5 py-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className={typographyTokens.eyebrow}>핵심 지표</p>
          <h3 className="mt-1 text-base font-semibold tracking-normal">
            지수, 금리, 환율을 먼저 확인합니다.
          </h3>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            시장 방향보다 무엇이 움직였는지 먼저 보면 종목 판단이 쉬워집니다.
          </p>
        </div>
        <Link
          href="/history"
          className="inline-flex h-9 items-center justify-center rounded-md border border-border/80 bg-muted/10 px-4 text-sm font-semibold transition hover:border-primary/35 hover:text-primary"
        >
          과거 흐름 보기
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
                "group flex min-h-[172px] flex-col justify-between px-5 py-4 transition hover:bg-muted/10",
                !isLast && "border-b border-border/80 xl:border-b-0 xl:border-r"
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-medium text-muted-foreground">
                    {item.category}
                  </p>
                  <h3 className="mt-1 text-base font-semibold tracking-normal">
                    {item.name}
                  </h3>
                  <p className="mt-1 text-xs text-muted-foreground">{item.symbol}</p>
                </div>
                <TrendChip direction={direction} value={item.changePercent} />
              </div>

              <div className="mt-5">
                <p className="numeric text-[1.45rem] font-semibold tracking-normal">
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
