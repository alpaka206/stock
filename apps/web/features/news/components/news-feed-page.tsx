import Link from "next/link";

import { DataSourceNotice } from "@/components/research/data-source-notice";
import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { NewsFeedArticle, NewsFeedFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";

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
      description: "시황 해석에 바로 영향을 주는 메인 뉴스를 먼저 본다.",
      items: data.featuredNews,
      empty: "현재 해외 헤드라인이 없습니다.",
    },
    {
      key: "watchlist",
      title: "관심종목 뉴스",
      description: "레이더 종목과 바로 연결되는 뉴스만 분리한다.",
      items: data.watchlistNews,
      empty: "관심종목 뉴스가 없습니다.",
    },
    {
      key: "domestic",
      title: "국내 공시",
      description: "OpenDART 연동으로 국내 행복 이벤트를 보조 피드로 제공한다.",
      items: data.domesticDisclosures,
      empty: "표시할 국내 공시가 없습니다.",
    },
  ].filter((section) => scope === "all" || scope === section.key);

  return (
    <div className={layoutTokens.page}>
      <section className="flex flex-col gap-4 rounded-[calc(var(--radius)*1.5)] border border-border/60 bg-[radial-gradient(circle_at_top_left,color-mix(in_oklch,var(--primary)_12%,transparent),transparent_50%),linear-gradient(180deg,color-mix(in_oklch,var(--background)_88%,var(--card))_0%,var(--background)_100%)] p-[var(--card-padding)]">
        <div className="max-w-3xl">
          <p className={typographyTokens.eyebrow}>뉴스 / 요약</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight lg:text-3xl">
            해외 뉴스, 관심종목 속보, 국내 공시를 한 흐름으로 보는 피드
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground lg:text-base">
            {data.marketSummary}
          </p>
          <DataSourceNotice source={data.dataSource} className="mt-4 max-w-2xl" />
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/overview" className={cn(buttonVariants({ size: "sm" }))}>
            시황 대시보드
          </Link>
          <Link href="/calendar" className={cn(buttonVariants({ size: "sm", variant: "outline" }))}>
            캘린더 보기
          </Link>
        </div>
      </section>

      <section className="grid gap-3 lg:grid-cols-3">
        {data.drivers.map((driver) => (
          <Link
            key={`${driver.label}-${driver.text}`}
            href={driver.href}
            className="rounded-[calc(var(--radius)*1.1)] border border-border/60 bg-background/65 p-4 transition hover:border-primary/30 hover:bg-background/90"
          >
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              {driver.label}
            </p>
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
              "rounded-full border px-3 py-1.5 text-sm font-semibold transition-colors",
              scope === option.value
                ? "border-primary/35 bg-primary/10 text-foreground"
                : "border-border/70 bg-background/45 text-muted-foreground hover:bg-muted/60"
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
                <div className="rounded-[calc(var(--radius)*1.05)] border border-dashed border-border/70 bg-background/20 p-4 text-sm leading-6 text-muted-foreground">
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
  const stockHref = item.symbol && item.market !== "domestic" ? `/stocks/${item.symbol}` : null;

  return (
    <article className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>{item.source}</span>
            <span>{formatPublishedAt(item.publishedAt)}</span>
            {item.symbol ? <span className="numeric">{item.symbol}</span> : null}
          </div>
          <p className="mt-2 text-sm font-semibold leading-6 tracking-tight">{item.headline}</p>
        </div>
        <span className={cn("shrink-0 rounded-full px-2.5 py-1 text-[0.68rem] font-semibold", getImpactTone(item.impact))}>
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
  if (normalized.includes("긍정") || normalized.includes("관심") || normalized.includes("positive")) {
    return "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]";
  }
  if (normalized.includes("부정") || normalized.includes("리스크") || normalized.includes("negative")) {
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
