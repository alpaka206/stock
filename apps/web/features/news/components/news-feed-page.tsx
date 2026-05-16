import Link from "next/link";

import { DataSourceNotice } from "@/components/research/data-source-notice";
import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import type { NewsFeedArticle, NewsFeedFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type NewsFeedPageProps = {
  data: NewsFeedFixture;
  scope: string;
};

const scopeOptions = [
  { value: "all", label: "전체", href: "/news" },
  { value: "global", label: "해외 헤드라인", href: "/news?scope=global" },
  { value: "watchlist", label: "관심종목", href: "/news?scope=watchlist" },
  { value: "domestic", label: "국내 공시", href: "/news?scope=domestic" },
] as const;

export function NewsFeedPage({ data, scope }: NewsFeedPageProps) {
  const sections = [
    {
      key: "global",
      title: "해외 헤드라인",
      description: "시장 방향에 영향을 주는 주요 글로벌 뉴스를 먼저 보여줍니다.",
      items: data.featuredNews,
      empty: "표시할 해외 헤드라인이 없습니다.",
    },
    {
      key: "watchlist",
      title: "관심종목 뉴스",
      description: "레이더에 담은 종목과 직접 연결되는 기사만 따로 모았습니다.",
      items: data.watchlistNews,
      empty: "관심종목 뉴스가 없습니다.",
    },
    {
      key: "domestic",
      title: "국내 공시",
      description: "OpenDART 연동 자료를 공시 흐름으로 확인할 수 있게 정리합니다.",
      items: data.domesticDisclosures,
      empty: "표시할 국내 공시가 없습니다.",
    },
  ].filter((section) => scope === "all" || scope === section.key);

  return (
    <div className={layoutTokens.page}>
      <section className="rounded-lg border border-border/60 bg-card p-[var(--card-padding)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className={typographyTokens.eyebrow}>뉴스 / 공시</p>
            <h1 className="mt-2 text-2xl font-semibold leading-tight lg:text-3xl">
              시장 뉴스와 공시를 투자 판단 흐름에 맞게 정리
            </h1>
            <p className="mt-3 text-sm leading-6 text-muted-foreground lg:text-base">
              {data.marketSummary}
            </p>
            <DataSourceNotice source={data.dataSource} className="mt-4 max-w-2xl" />
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/overview" className={cn(buttonVariants({ size: "sm" }))}>
              시장 대시보드
            </Link>
            <Link href="/calendar" className={cn(buttonVariants({ size: "sm", variant: "outline" }))}>
              캘린더 보기
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-3 lg:grid-cols-3">
        {data.drivers.map((driver) => (
          <Link
            key={`${driver.label}-${driver.text}`}
            href={driver.href}
            className="rounded-md border border-border/60 bg-background p-4 transition-colors hover:border-primary/35 hover:bg-muted/35"
          >
            <p className="text-xs font-semibold uppercase text-muted-foreground">{driver.label}</p>
            <p className="mt-2 text-sm leading-6 text-foreground">{driver.text}</p>
          </Link>
        ))}
      </section>

      <div className="flex flex-wrap gap-2">
        {scopeOptions.map((option) => (
          <Link
            key={option.value}
            href={option.href}
            className={cn(
              "rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
              scope === option.value
                ? "border-primary/35 bg-primary/10 text-foreground"
                : "border-border/70 bg-background text-muted-foreground hover:bg-muted/50"
            )}
          >
            {option.label}
          </Link>
        ))}
      </div>

      <section className="grid gap-[var(--space-grid)] xl:grid-cols-3">
        {sections.map((section) => (
          <ResearchPanel key={section.key} title={section.title} description={section.description}>
            <div className="space-y-3">
              {section.items.length === 0 ? (
                <div className="rounded-md border border-dashed border-border/70 bg-background p-4 text-sm leading-6 text-muted-foreground">
                  {section.empty}
                </div>
              ) : null}
              {section.items.map((item) => (
                <ArticleCard key={item.id} item={item} />
              ))}
            </div>
          </ResearchPanel>
        ))}
      </section>
    </div>
  );
}

function ArticleCard({ item }: { item: NewsFeedArticle }) {
  const stockHref =
    item.symbol && item.market !== "domestic" ? `/stocks/${item.symbol}` : null;

  return (
    <article className="rounded-md border border-border/60 bg-background p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>{item.source}</span>
            <span>{formatPublishedAt(item.publishedAt)}</span>
            {item.symbol ? <span className="numeric">{item.symbol}</span> : null}
          </div>
          <h2 className="mt-2 text-sm font-semibold leading-6">{item.headline}</h2>
        </div>
        <span
          className={cn(
            "shrink-0 rounded-md px-2.5 py-1 text-xs font-semibold",
            getImpactTone(item.impact)
          )}
        >
          {item.impact}
        </span>
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.summary}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {stockHref ? (
          <Link href={stockHref} className={cn(buttonVariants({ size: "sm", variant: "outline" }))}>
            종목 보기
          </Link>
        ) : null}
        {item.url ? (
          <a
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className={cn(buttonVariants({ size: "sm", variant: "ghost" }))}
          >
            원문 보기
          </a>
        ) : null}
      </div>
    </article>
  );
}

function getImpactTone(impact: string) {
  const normalized = impact.toLowerCase();
  if (
    normalized.includes("긍정") ||
    normalized.includes("상승") ||
    normalized.includes("positive")
  ) {
    return "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]";
  }
  if (
    normalized.includes("부정") ||
    normalized.includes("위험") ||
    normalized.includes("negative")
  ) {
    return "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]";
  }
  return "bg-muted text-muted-foreground";
}

function formatPublishedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
