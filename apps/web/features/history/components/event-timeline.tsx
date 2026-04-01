"use client";

import type { HistoryEvent } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type EventTimelineProps = {
  events: HistoryEvent[];
  selectedId?: string;
  onSelect?: (eventId: string) => void;
};

export function EventTimeline({
  events,
  selectedId,
  onSelect,
}: EventTimelineProps) {
  return (
    <div className="space-y-3">
      {events.map((event) => {
        const active = event.id === selectedId;

        return (
          <button
            key={event.id}
            type="button"
            onClick={() => onSelect?.(event.id)}
            className={cn(
              "flex w-full flex-col gap-2 rounded-[calc(var(--radius)*1.05)] border px-4 py-3 text-left transition-colors",
              active
                ? "border-primary/35 bg-primary/10"
                : "border-border/60 bg-background/25 hover:bg-muted/60"
            )}
          >
            <div className="flex items-center justify-between gap-3">
              <span className="numeric text-xs text-muted-foreground">
                {event.date}
              </span>
              <span
                className={cn(
                  "rounded-full px-2 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em]",
                  event.tone === "positive"
                    ? "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]"
                    : event.tone === "negative"
                      ? "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]"
                      : "bg-muted text-muted-foreground"
                )}
              >
                {event.category}
              </span>
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight">{event.title}</p>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">
                {event.summary}
              </p>
            </div>
            {event.source ? (
              <p className="text-xs text-muted-foreground">{event.source}</p>
            ) : null}
            <p className="numeric text-xs font-semibold text-foreground/80">
              {event.reaction}
            </p>
          </button>
        );
      })}
    </div>
  );
}
