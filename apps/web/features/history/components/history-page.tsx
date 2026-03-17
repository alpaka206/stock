"use client";

import * as React from "react";

import { ResearchPanel } from "@/components/research/research-panel";
import { ResearchLineChart } from "@/features/chart/components/research-line-chart";
import { FilterChipGroup } from "@/features/filters/components/filter-chip-group";
import { EventTimeline } from "@/features/history/components/event-timeline";
import type { HistoryFixture } from "@/lib/research/types";
import { layoutTokens, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type HistoryPageProps = {
  history: HistoryFixture;
};

export function HistoryPage({ history }: HistoryPageProps) {
  const [activePreset, setActivePreset] = React.useState(
    history.presets[1] ?? history.presets[0]
  );
  const [selectedEventId, setSelectedEventId] = React.useState(
    history.events[0]?.id
  );

  const selectedEvent =
    history.events.find((event) => event.id === selectedEventId) ??
    history.events[0];

  return (
    <div className={layoutTokens.page}>
      <ResearchPanel
        title="히스토리 필터 바"
        description="종목, 날짜 범위, 이벤트 구간 프리셋"
      >
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className={typographyTokens.eyebrow}>{history.symbol}</p>
            <p className="numeric mt-1 text-sm font-semibold">{history.range}</p>
          </div>
          <FilterChipGroup
            options={history.presets.map((preset) => ({
              value: preset,
              label: preset,
            }))}
            value={activePreset}
            onValueChange={setActivePreset}
          />
        </div>
      </ResearchPanel>

      <div className={layoutTokens.splitPanelGrid}>
        <ResearchPanel
          title="리플레이 차트"
          description={
            selectedEvent
              ? `${selectedEvent.date} · ${selectedEvent.title}`
              : `${history.symbol} 과거 이벤트 리플레이`
          }
        >
          <div className="space-y-4">
            <p className="text-sm leading-6 text-muted-foreground">
              {selectedEvent
                ? selectedEvent.summary
                : "과거 변곡점을 이벤트와 함께 되짚는 화면"}
            </p>
            <ResearchLineChart points={history.chartPoints} accent="primary" />
          </div>
        </ResearchPanel>

        <ResearchPanel
          title="이벤트 타임라인"
          description={`현재 프리셋: ${activePreset}`}
        >
          <EventTimeline
            events={history.events}
            selectedId={selectedEventId}
            onSelect={setSelectedEventId}
          />
        </ResearchPanel>
      </div>

      <div className="grid gap-[var(--space-grid)] lg:grid-cols-2">
        <ResearchPanel title="이유 요약 카드" description="왜 그날 움직였는지">
          <div className="space-y-3">
            {history.moveReasons.map((reason) => (
              <div
                key={reason.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4"
              >
                <p className="text-sm font-semibold tracking-tight">
                  {reason.label}
                </p>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {reason.description}
                </p>
              </div>
            ))}
          </div>
        </ResearchPanel>

        <ResearchPanel title="중복 지표 설명 카드" description="변곡점에 겹친 신호">
          <div className="space-y-3">
            {history.overlaps.map((overlap) => (
              <div
                key={overlap.label}
                className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold tracking-tight">
                    {overlap.label}
                  </p>
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
              </div>
            ))}
          </div>
        </ResearchPanel>
      </div>
    </div>
  );
}
