"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";

import { InstrumentSearch } from "@/components/research/instrument-search";
import { ResearchPanel } from "@/components/research/research-panel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ResearchLineChart } from "@/features/chart/components/research-line-chart";
import { EventTimeline } from "@/features/history/components/event-timeline";
import { useRecentSymbols } from "@/lib/client/use-recent-symbols";
import { useUrlState } from "@/lib/client/use-url-state";
import type { HistoryFixture } from "@/lib/research/types";
import { layoutTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type HistoryPageProps = {
  history: HistoryFixture;
};

export function HistoryPage({ history }: HistoryPageProps) {
  const router = useRouter();
  const { searchParams, replaceParams } = useUrlState();
  const { symbols: recentSymbols, pushSymbol } = useRecentSymbols(
    "stock-workspace:history-recent-symbols",
    [history.symbol]
  );

  React.useEffect(() => {
    pushSymbol(history.symbol);
  }, [history.symbol, pushSymbol]);

  const selectedEventId =
    searchParams.get("event") ??
    history.events[0]?.id ??
    history.eventMarkers[0]?.id ??
    "";
  const selectedEvent =
    history.events.find((event) => event.id === selectedEventId) ?? history.events[0];
  const selectedEventIndex = Math.max(
    0,
    history.events.findIndex((event) => event.id === selectedEvent?.id)
  );
  const previousEvent = history.events[selectedEventIndex - 1];
  const nextEvent = history.events[selectedEventIndex + 1];
  const selectedRange =
    history.availableRanges.find((range) => range.value === searchParams.get("range"))
      ?.value ?? history.availableRanges[0]?.value;
  const fromValue = searchParams.get("from") ?? "";
  const toValue = searchParams.get("to") ?? "";

  return (
    <div className={layoutTokens.page}>
      <ResearchPanel
        title="히스토리 / 이벤트 리플레이"
        description="종목과 날짜 범위를 바꾸면서 과거 급등·급락 이유를 다시 읽는다."
      >
        <div className="space-y-4">
          <InstrumentSearch
            selectedSymbol={history.symbol}
            label="기록 다시 보기"
            helperText="종목을 바꾸면 해당 심볼의 이벤트 리플레이로 이동한다."
            quickSymbols={recentSymbols}
            onSelect={(instrument) => {
              const nextQuery = new URLSearchParams(searchParams.toString());
              nextQuery.set("symbol", instrument.symbol);
              router.push(`/history?${nextQuery.toString()}`);
            }}
          />
          <div className="grid gap-3 xl:grid-cols-[180px_1fr_1fr]">
            <Select
              value={selectedRange}
              onValueChange={(value) => replaceParams({ range: value, event: undefined })}
            >
              <SelectTrigger className="w-full bg-background/65">
                <SelectValue placeholder="구간" />
              </SelectTrigger>
              <SelectContent>
                {history.availableRanges.map((range) => (
                  <SelectItem key={range.value} value={range.value}>
                    {range.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="date"
              value={fromValue}
              onChange={(event) => replaceParams({ from: event.target.value })}
              className="bg-background/70"
            />
            <Input
              type="date"
              value={toValue}
              onChange={(event) => replaceParams({ to: event.target.value })}
              className="bg-background/70"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <span className="numeric font-semibold">{history.range}</span>
            <span>·</span>
            <span>{history.moveSummary}</span>
          </div>
        </div>
      </ResearchPanel>

      <div className="grid gap-[var(--space-grid)] xl:grid-cols-[minmax(0,1.3fr)_380px]">
        <ResearchPanel
          title="과거 차트 리플레이"
          description={
            selectedEvent
              ? `${selectedEvent.date} · ${selectedEvent.title}`
              : `${history.symbol} 과거 이벤트 리플레이`
          }
        >
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-sm leading-6 text-muted-foreground">
                  {selectedEvent
                    ? selectedEvent.summary
                    : "과거 변곡점을 선택하면 차트와 타임라인이 동시에 이동한다."}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!previousEvent}
                  onClick={() =>
                    previousEvent
                      ? replaceParams({ event: previousEvent.id })
                      : undefined
                  }
                >
                  <ChevronLeft />
                  이전
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!nextEvent}
                  onClick={() =>
                    nextEvent ? replaceParams({ event: nextEvent.id }) : undefined
                  }
                >
                  다음
                  <ChevronRight />
                </Button>
              </div>
            </div>

            <ResearchLineChart
              points={history.priceSeries}
              markers={history.eventMarkers}
              activePointKey={selectedEvent?.date}
              highlightRange={
                selectedEvent
                  ? { startKey: selectedEvent.date, endKey: selectedEvent.date }
                  : undefined
              }
              onPointSelect={(pointKey) => {
                const matchedEvent = history.events.find((event) => event.date === pointKey);

                if (matchedEvent) {
                  replaceParams({ event: matchedEvent.id });
                }
              }}
              accent="primary"
            />
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="이벤트 / 뉴스 타임라인"
          description="특정 이벤트를 누르면 차트 포커스가 바로 이동한다."
        >
          <EventTimeline
            events={history.events}
            selectedId={selectedEvent?.id}
            onSelect={(eventId) => replaceParams({ event: eventId })}
          />
        </ResearchPanel>
      </div>

      <div className="grid gap-[var(--space-grid)] xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <ResearchPanel title="급등 / 급락 이유 요약" description="과거 움직임 이유를 카드로 다시 읽는다.">
          <div className="space-y-3">
            {history.moveReasons.map((reason) => (
              <div
                key={reason.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">{reason.label}</p>
                  {reason.relatedDate ? (
                    <span className="numeric text-xs text-muted-foreground">
                      {reason.relatedDate}
                    </span>
                  ) : null}
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {reason.description}
                </p>
              </div>
            ))}
          </div>
        </ResearchPanel>

        <ResearchPanel title="중복 지표 설명 카드" description="변곡점에서 겹친 보조지표 신호를 함께 본다.">
          <div className="space-y-3">
            {history.overlaps.map((overlap) => (
              <div
                key={overlap.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">{overlap.label}</p>
                  <span
                    className={cn(
                      "rounded-full px-2 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em]",
                      overlap.tone === "positive"
                        ? "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]"
                        : overlap.tone === "negative"
                          ? "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]"
                          : "bg-muted text-muted-foreground"
                    )}
                  >
                    {overlap.tone === "positive"
                      ? "강세"
                      : overlap.tone === "negative"
                        ? "주의"
                        : "중립"}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {overlap.detail}
                </p>
                {overlap.relatedDate ? (
                  <p className="numeric mt-2 text-xs text-muted-foreground">
                    관련 날짜 {overlap.relatedDate}
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </ResearchPanel>
      </div>
    </div>
  );
}
