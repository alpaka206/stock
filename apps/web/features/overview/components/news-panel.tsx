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
      title="뉴스 패널"
      description="시장 해석을 바꿀 headline만 먼저 읽는다"
      action={
        <Link
          href="/news"
          className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
        >
          뉴스 피드
        </Link>
      }
    >
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-[calc(var(--radius)*1.05)] border border-dashed border-border/70 bg-background/20 p-4 text-sm leading-6 text-muted-foreground">
            현재 연결된 뉴스 요약이 없습니다. 뉴스 피드와 히스토리 화면에서 출처와 누락 데이터를 함께 확인해 주세요.
          </div>
        ) : null}
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href ?? "/history"}
            className="block rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4 transition hover:border-primary/30 hover:bg-background/45"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{item.source}</span>
                  <span className="numeric">{item.publishedAt}</span>
                </div>
                <p className="mt-2 text-sm font-semibold leading-6 tracking-tight">
                  {item.headline}
                </p>
              </div>
              <span
                className={cn(
                  "shrink-0 rounded-full px-2.5 py-1 text-[0.68rem] font-semibold",
                  getToneBadge(item.tone)
                )}
              >
                {item.impactLabel}
              </span>
            </div>

            {item.summary ? (
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                {item.summary}
              </p>
            ) : null}

            <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary">
              전체 피드에서 계속 보기
              <ArrowUpRight className="size-3.5" />
            </p>
          </Link>
        ))}
      </div>
    </ResearchPanel>
  );
}

function getToneBadge(tone: Tone) {
  if (tone === "positive") {
    return "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]";
  }

  if (tone === "negative") {
    return "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]";
  }

  return "bg-muted text-muted-foreground";
}
