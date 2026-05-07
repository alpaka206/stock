import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import type { NewsItem, Tone } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type NewsPanelProps = {
  items: NewsItem[];
};

export function NewsPanel({ items }: NewsPanelProps) {
  return (
    <ResearchPanel
      eyebrow="Headline Flow"
      title="헤드라인 플로우"
      description="시장 해석을 바꿀 수 있는 기사만 시간순으로 압축해 읽습니다."
      action={
        <Link
          href="/news"
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "rounded-[calc(var(--radius)*0.72)]"
          )}
        >
          전체 뉴스
        </Link>
      }
      variant="feed"
    >
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-[calc(var(--radius)*0.82)] border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
            현재 헤드라인 플로우를 구성할 기사 요약이 없습니다. 뉴스 원문과
            히스토리에서 직접 확인해 주세요.
          </div>
        ) : null}

        {items.length > 0 ? (
          <div className="divide-y divide-border/80">
            {items.map((item) => (
              <Link
                key={item.id}
                href={item.href ?? "/history"}
                className="group block py-4 first:pt-0 last:pb-0"
              >
                <div className="grid gap-3 md:grid-cols-[88px_minmax(0,1fr)_108px] md:items-start">
                  <div className="text-xs text-muted-foreground">
                    <p className="font-semibold uppercase tracking-[0.18em] text-muted-foreground/75">
                      {item.source}
                    </p>
                    <p className="numeric mt-1">{item.publishedAt}</p>
                  </div>

                  <div className="min-w-0">
                    <p className="text-sm font-semibold leading-6 tracking-tight text-foreground">
                      {item.headline}
                    </p>
                    {item.summary ? (
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        {item.summary}
                      </p>
                    ) : null}
                  </div>

                  <div className="flex items-center justify-between gap-3 md:block md:text-right">
                    <span
                      className={cn(
                        "inline-flex rounded-[0.42rem] border px-2.5 py-1 text-[0.68rem] font-semibold",
                        getToneBadge(item.tone)
                      )}
                    >
                      {item.impactLabel}
                    </span>
                    <p className="mt-0 text-xs font-semibold text-primary md:mt-3">
                      이어서 읽기
                      <ArrowUpRight className="ml-1 inline size-3.5 align-middle" />
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

function getToneBadge(tone: Tone) {
  if (tone === "positive") {
    return "border-[color:color-mix(in_oklch,var(--positive)_20%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)] text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "border-[color:color-mix(in_oklch,var(--negative)_20%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)] text-[color:var(--negative)]";
  }

  return "border-border/80 bg-muted/15 text-muted-foreground";
}
