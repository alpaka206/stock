import type { ResearchDataSource } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type DataSourceNoticeProps = {
  source: ResearchDataSource;
  className?: string;
};

const toneClassMap: Record<ResearchDataSource["mode"], string> = {
  live: "border-[color:color-mix(in_oklch,var(--positive)_35%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)] text-foreground",
  mock: "border-[color:color-mix(in_oklch,var(--warning)_35%,transparent)] bg-[color:color-mix(in_oklch,var(--warning)_10%,transparent)] text-foreground",
  fixture: "border-border/70 bg-background/70 text-foreground",
  "fixture-fallback":
    "border-[color:color-mix(in_oklch,var(--negative)_35%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)] text-foreground",
};

export function DataSourceNotice({ source, className }: DataSourceNoticeProps) {
  return (
    <div
      className={cn(
        "rounded-[calc(var(--radius)*1.05)] border px-3 py-2.5",
        toneClassMap[source.mode],
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          데이터 상태
        </span>
        <span className="text-sm font-semibold tracking-tight">{source.label}</span>
      </div>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">{source.description}</p>
    </div>
  );
}
