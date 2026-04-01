import {
  ArrowDownRight,
  ArrowUpRight,
  Minus,
  type LucideIcon,
} from "lucide-react";

import { formatSignedPercent } from "@/lib/format";
import type { TrendDirection } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type TrendChipProps = {
  direction: TrendDirection;
  value: number;
  className?: string;
};

const iconByDirection: Record<TrendDirection, LucideIcon> = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  flat: Minus,
};

const toneByDirection: Record<TrendDirection, string> = {
  up: "tone-positive border-[color:color-mix(in_oklch,var(--positive)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)]",
  down: "tone-negative border-[color:color-mix(in_oklch,var(--negative)_32%,transparent)] bg-[color:color-mix(in_oklch,var(--negative)_10%,transparent)]",
  flat: "tone-neutral border-border/70 bg-muted/70",
};

export function TrendChip({ direction, value, className }: TrendChipProps) {
  const Icon = iconByDirection[direction];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold",
        toneByDirection[direction],
        className
      )}
    >
      <Icon className="size-3.5" />
      <span className="numeric">{formatSignedPercent(value)}</span>
    </span>
  );
}
