"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAppLanguage } from "@/components/providers/language-provider";
import { DataSourceNotice } from "@/components/research/data-source-notice";
import { InstrumentSearch } from "@/components/research/instrument-search";
import { ResearchPanel } from "@/components/research/research-panel";
import { ResearchSnapshotCard } from "@/components/research/research-snapshot-card";
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
import { useResearchSnapshots } from "@/lib/client/use-research-snapshots";
import { useUrlState } from "@/lib/client/use-url-state";
import type { HistoryFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type HistoryPageProps = {
  history: HistoryFixture;
};

export function HistoryPage({ history }: HistoryPageProps) {
  const router = useRouter();
  const { messages } = useAppLanguage();
  const copy = messages.history;
  const { searchParams, replaceParams } = useUrlState();
  const { symbols: recentSymbols, pushSymbol } = useRecentSymbols(
    "stock-workspace:history-recent-symbols",
    [history.symbol]
  );
  const { snapshots, removeSnapshot } = useResearchSnapshots();

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
  const fromValue = searchParams.get("from") ?? "";
  const toValue = searchParams.get("to") ?? "";
  const hasCustomRange = Boolean(fromValue || toValue);
  const selectedRange =
    history.availableRanges.find((range) => range.value === searchParams.get("range"))
      ?.value ??
    (hasCustomRange ? "custom" : history.availableRanges[0]?.value ?? "3m");
  const symbolSnapshots = React.useMemo(
    () => snapshots.filter((snapshot) => snapshot.symbol === history.symbol),
    [history.symbol, snapshots]
  );

  return (
    <div className={layoutTokens.page} data-testid="history-page">
      <ResearchPanel title={copy.title} description={copy.description}>
        <div className="space-y-4">
          <DataSourceNotice source={history.dataSource} />
          <InstrumentSearch
            selectedSymbol={history.symbol}
            label={copy.searchLabel}
            helperText={copy.searchHelper}
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
              onValueChange={(value) =>
                replaceParams({
                  range: value === "custom" ? undefined : value,
                  from: undefined,
                  to: undefined,
                  event: undefined,
                })
              }
            >
              <SelectTrigger className="w-full bg-background/65">
                <SelectValue placeholder={copy.rangePlaceholder} />
              </SelectTrigger>
              <SelectContent>
                {hasCustomRange ? (
                  <SelectItem value="custom">{copy.customRange}</SelectItem>
                ) : null}
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
              onChange={(event) =>
                replaceParams({
                  from: event.target.value,
                  range: undefined,
                  event: undefined,
                })
              }
            />
            <Input
              type="date"
              value={toValue}
              onChange={(event) =>
                replaceParams({
                  to: event.target.value,
                  range: undefined,
                  event: undefined,
                })
              }
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
          title={copy.replayTitle}
          description={
            selectedEvent
              ? `${selectedEvent.date} · ${selectedEvent.title}`
              : `${history.symbol} ${copy.replayTitle}`
          }
        >
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
                {selectedEvent ? selectedEvent.summary : copy.replayFallback}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!previousEvent}
                  onClick={() =>
                    previousEvent ? replaceParams({ event: previousEvent.id }) : undefined
                  }
                >
                  <ChevronLeft className="size-4" />
                  {messages.common.previous}
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
                  {messages.common.next}
                  <ChevronRight className="size-4" />
                </Button>
              </div>
            </div>

            <ResearchLineChart
              testId="history-price-chart"
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

        <ResearchPanel title={copy.timelineTitle} description={copy.timelineDescription}>
          <EventTimeline
            events={history.events}
            selectedId={selectedEvent?.id}
            onSelect={(eventId) => replaceParams({ event: eventId })}
          />
        </ResearchPanel>
      </div>

      <div className="grid gap-[var(--space-grid)] xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <ResearchPanel title={copy.moveTitle} description={copy.moveDescription}>
          <div className="space-y-3">
            {history.moveReasons.map((reason, index) => (
              <div
                key={`${reason.label}-${reason.relatedDate ?? index}`}
                className="rounded-lg border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold">{reason.label}</p>
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

        <ResearchPanel title={copy.overlapTitle} description={copy.overlapDescription}>
          <div className="space-y-3">
            {history.overlaps.map((overlap, index) => (
              <div
                key={`${overlap.label}-${overlap.relatedDate ?? index}`}
                className="rounded-lg border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold">{overlap.label}</p>
                  <span
                    className={cn(
                      "rounded-md px-2 py-1 text-[0.68rem] font-semibold",
                      overlap.tone === "positive"
                        ? "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]"
                        : overlap.tone === "negative"
                          ? "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]"
                          : "bg-muted text-muted-foreground"
                    )}
                  >
                    {overlap.tone === "positive"
                      ? copy.tonePositive
                      : overlap.tone === "negative"
                        ? copy.toneNegative
                        : copy.toneNeutral}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {overlap.detail}
                </p>
                {overlap.relatedDate ? (
                  <p className="numeric mt-2 text-xs text-muted-foreground">
                    {messages.common.relatedDate} {overlap.relatedDate}
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </ResearchPanel>
      </div>

      <ResearchPanel
        title={copy.journalTitle}
        description={`${history.symbol} ${copy.journalDescription}`}
      >
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className={cn(typographyTokens.eyebrow, "normal-case")}>
              {copy.savedCount(symbolSnapshots.length)}
            </p>
            <Button asChild variant="outline" size="sm">
              <Link href={`/stocks/${history.symbol}`}>{copy.goToDetail}</Link>
            </Button>
          </div>

          {symbolSnapshots.length > 0 ? (
            <div className="grid gap-3 xl:grid-cols-2">
              {symbolSnapshots.map((snapshot) => (
                <ResearchSnapshotCard
                  key={snapshot.id}
                  snapshot={snapshot}
                  actions={
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => removeSnapshot(snapshot.id)}
                    >
                      {messages.common.delete}
                    </Button>
                  }
                />
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-border/60 px-4 py-5 text-sm leading-6 text-muted-foreground">
              {copy.journalEmpty}
            </div>
          )}
        </div>
      </ResearchPanel>
    </div>
  );
}
