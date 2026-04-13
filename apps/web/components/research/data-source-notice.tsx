import type { ResearchDataSource } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type DataSourceNoticeProps = {
  source: ResearchDataSource;
  className?: string;
};

const toneClassMap: Record<Exclude<ResearchDataSource["mode"], "live">, string> = {
  mock: "border-[color:color-mix(in_oklch,var(--warning)_35%,transparent)] bg-[color:color-mix(in_oklch,var(--warning)_10%,transparent)] text-foreground",
  fixture: "border-border/70 bg-background/70 text-foreground",
  "fixture-fallback":
    "border-[color:color-mix(in_oklch,var(--negative)_35%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)] text-foreground",
};

export function DataSourceNotice({ source, className }: DataSourceNoticeProps) {
  if (source.mode === "live") {
    return null;
  }

  return (
    <div
      className={cn(
        "rounded-[calc(var(--radius)*1.05)] border px-3 py-2",
        toneClassMap[source.mode],
        className
      )}
    >
      <p className="text-sm font-semibold tracking-tight">{source.label}</p>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">{source.description}</p>
    </div>
  );
}
