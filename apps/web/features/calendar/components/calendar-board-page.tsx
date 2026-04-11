import Link from "next/link";

import { DataSourceNotice } from "@/components/research/data-source-notice";
import { ResearchPanel } from "@/components/research/research-panel";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { CalendarEventItem, CalendarFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";

type CalendarBoardPageProps = {
  data: CalendarFixture;
  scope: string;
};

const scopeOptions = [
  { value: "all", label: "전체", href: "/calendar" },
  { value: "watchlist", label: "관심종목", href: "/calendar?scope=watchlist" },
  { value: "market", label: "IPO / 시장", href: "/calendar?scope=market" },
  { value: "domestic", label: "국내 공시", href: "/calendar?scope=domestic" },
] as const;

export function CalendarBoardPage({ data, scope }: CalendarBoardPageProps) {
  const sections = [
    {
      key: "watchlist",
      title: "관심종목 일정",
      description: "레이더 종목 중심으로 실적과 뉴스 체크 포인트를 묶는다.",
      items: data.watchlistEvents,
      empty: "표시할 관심종목 일정이 없습니다.",
    },
    {
      key: "market",
      title: "IPO / 시장 이벤트",
      description: "글로벌 IPO와 시장 체크 이벤트를 분리해 본다.",
      items: data.marketEvents,
      empty: "표시할 시장 이벤트가 없습니다.",
    },
    {
      key: "domestic",
      title: "국내 공시",
      description: "OpenDART 기준 최신 공시를 일정 흐름으로 확인한다.",
      items: data.domesticEvents,
      empty: "표시할 국내 공시가 없습니다.",
    },
  ].filter((section) => scope === "all" || scope === section.key);

  return (
    <div className={layoutTokens.page}>
      <section className="flex flex-col gap-4 rounded-[calc(var(--radius)*1.5)] border border-border/60 bg-[radial-gradient(circle_at_top_left,color-mix(in_oklch,var(--primary)_12%,transparent),transparent_50%),linear-gradient(180deg,color-mix(in_oklch,var(--background)_88%,var(--card))_0%,var(--background)_100%)] p-[var(--card-padding)]">
        <div className="max-w-3xl">
          <p className={typographyTokens.eyebrow}>일정 / 실적</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight lg:text-3xl">
            실적, IPO, 국내 공시, 뉴스 체크 포인트를 한 화면에서 보는 캘린더
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground lg:text-base">
            {data.summary}
          </p>
          <DataSourceNotice source={data.dataSource} className="mt-4 max-w-2xl" />
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/overview" className={cn(buttonVariants({ size: "sm" }))}>
            시황 대시보드
          </Link>
          <Link href="/news" className={cn(buttonVariants({ size: "sm", variant: "outline" }))}>
            뉴스 피드
          </Link>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {data.highlights.map((item) => (
          <div key={item.label} className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/35 p-4">
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">{item.label}</p>
            <p className="numeric mt-2 text-2xl font-semibold">{item.value}</p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.detail}</p>
          </div>
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
                <EventCard key={item.id} item={item} />
              ))}
            </div>
          </ResearchPanel>
        ))}
      </section>
    </div>
  );
}

function EventCard({ item }: { item: CalendarEventItem }) {
  const stockHref = item.symbol && item.market !== "domestic" ? `/stocks/${item.symbol}` : null;
  return (
    <article className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/25 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>{item.source}</span>
            <span className="numeric">{item.date}</span>
            <span>{item.time}</span>
          </div>
          <p className="mt-2 text-sm font-semibold leading-6 tracking-tight">{item.title}</p>
        </div>
        <span className={cn("shrink-0 rounded-full px-2.5 py-1 text-[0.68rem] font-semibold", getTone(item.tone))}>
          {formatCategory(item.category)}
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

function getTone(tone: CalendarEventItem["tone"]) {
  if (tone === "positive") {
    return "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]";
  }
  if (tone === "negative") {
    return "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]";
  }
  return "bg-muted text-muted-foreground";
}

function formatCategory(category: CalendarEventItem["category"]) {
  if (category === "earnings") {
    return "실적";
  }
  if (category === "ipo") {
    return "IPO";
  }
  if (category === "disclosure") {
    return "공시";
  }
  if (category === "news") {
    return "뉴스";
  }
  return "매크로";
}
