import { formatSignedPercent } from "@/lib/format";
import { ResearchPanel } from "@/components/research/research-panel";
import { cn } from "@/lib/utils";

export type SectorSummaryPanelItem = {
  label: string;
  score: number;
  summary: string;
  meta?: string;
  changePercent?: number;
};

type SectorSummaryPanelProps = {
  title: string;
  description?: string;
  items: SectorSummaryPanelItem[];
  className?: string;
};

export function SectorSummaryPanel({
  title,
  description,
  items,
  className,
}: SectorSummaryPanelProps) {
  return (
    <ResearchPanel title={title} description={description} className={className}>
      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.label}
            className="rounded-[calc(var(--radius)*1.05)] border border-border/55 bg-background/30 p-3"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold tracking-tight">
                  {item.label}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{item.summary}</p>
              </div>
              <div className="text-right">
                <p className="numeric text-lg font-semibold">{item.score}</p>
                {item.changePercent !== undefined ? (
                  <p
                    className={cn(
                      "numeric text-xs",
                      item.changePercent > 0
                        ? "tone-positive"
                        : item.changePercent < 0
                          ? "tone-negative"
                          : "tone-neutral"
                    )}
                  >
                    {formatSignedPercent(item.changePercent)}
                  </p>
                ) : null}
              </div>
            </div>
            {item.meta ? (
              <p className="mt-2 text-xs text-muted-foreground">{item.meta}</p>
            ) : null}
          </div>
        ))}
      </div>
    </ResearchPanel>
  );
}
