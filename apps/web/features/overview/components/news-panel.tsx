import { ArrowUpRight } from "lucide-react";
import Link from "next/link";

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
      eyebrow="Headline flow"
      title="핵심 뉴스"
      description="시장 해석을 바꿀 수 있는 기사와 공시를 시간순으로 봅니다."
      action={
        <Link href="/news" className={buttonVariants({ variant: "outline", size: "sm" })}>
          전체 뉴스
        </Link>
      }
      variant="feed"
    >
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border/80 bg-muted/10 p-4 text-sm leading-6 text-muted-foreground">
            표시할 뉴스가 없습니다. 실제 API 연결 상태와 데이터 출처를 확인해 주세요.
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
                    <p className="font-semibold uppercase text-muted-foreground/75">
                      {item.source}
                    </p>
                    <p className="numeric mt-1">{item.publishedAt}</p>
                  </div>

                  <div className="min-w-0">
                    <p className="text-sm font-semibold leading-6 text-foreground">
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
                        "inline-flex rounded-md border px-2.5 py-1 text-[0.68rem] font-semibold",
                        getToneBadge(item.tone)
                      )}
                    >
                      {item.impactLabel}
                    </span>
                    <p className="mt-0 text-xs font-semibold text-primary md:mt-3">
                      자세히
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
