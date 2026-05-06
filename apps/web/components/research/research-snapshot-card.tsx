"use client";

import * as React from "react";

import { useAppLanguage } from "@/components/providers/language-provider";
import { researchSnapshotStanceTone } from "@/lib/client/use-research-snapshots";
import type { ResearchSnapshot } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type ResearchSnapshotCardProps = {
  snapshot: ResearchSnapshot;
  compact?: boolean;
  actions?: React.ReactNode;
};

export function ResearchSnapshotCard({
  snapshot,
  compact = false,
  actions,
}: ResearchSnapshotCardProps) {
  const { language, messages } = useAppLanguage();
  const stanceTone = researchSnapshotStanceTone[snapshot.stance];
  const stanceLabel = messages.stocks.stance[snapshot.stance];
  const convictionLabel = messages.stocks.conviction[snapshot.conviction];
  const snapshotDateFormatter = React.useMemo(
    () =>
      new Intl.DateTimeFormat(language === "ko" ? "ko-KR" : "en-US", {
        dateStyle: "medium",
        timeStyle: "short",
      }),
    [language]
  );

  return (
    <article className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "rounded-full px-2 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em]",
                stanceTone === "positive"
                  ? "bg-[color:color-mix(in_oklch,var(--positive)_14%,transparent)] text-[color:var(--positive)]"
                  : stanceTone === "negative"
                    ? "bg-[color:color-mix(in_oklch,var(--negative)_14%,transparent)] text-[color:var(--negative)]"
                    : "bg-muted text-muted-foreground"
              )}
            >
              {stanceLabel}
            </span>
            <span className="text-xs text-muted-foreground">
              {messages.common.confidence} {convictionLabel}
            </span>
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">
              {snapshot.symbol} · {snapshot.name}
            </p>
            <p className="text-xs text-muted-foreground">
              {snapshot.exchange} · {snapshot.securityCode} ·{" "}
              {snapshotDateFormatter.format(new Date(snapshot.createdAt))}
            </p>
          </div>
        </div>
        {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
      </div>

      <p className="mt-3 text-sm leading-6 text-foreground/92">
        {snapshot.note || messages.common.none}
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <span className="numeric font-semibold">${snapshot.price.toFixed(2)}</span>
        <span className="numeric">
          {snapshot.changePercent > 0 ? "+" : ""}
          {snapshot.changePercent.toFixed(2)}%
        </span>
        <span className="numeric">
          {messages.stocks.detail.scoreSummaryTitle} {snapshot.score}
        </span>
        {snapshot.selectedEventTitle ? (
          <span>
            {messages.history.timelineTitle} {snapshot.selectedEventTitle}
            {snapshot.selectedEventDate ? ` · ${snapshot.selectedEventDate}` : ""}
          </span>
        ) : null}
      </div>

      {!compact ? (
        <>
          <p className="mt-3 text-xs leading-5 text-muted-foreground">{snapshot.thesis}</p>
          {snapshot.activeRuleLabels.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {snapshot.activeRuleLabels.map((label) => (
                <span
                  key={label}
                  className="rounded-full border border-border/55 px-2 py-1 text-[0.68rem] text-muted-foreground"
                >
                  {label}
                </span>
              ))}
            </div>
          ) : null}
        </>
      ) : null}
    </article>
  );
}
