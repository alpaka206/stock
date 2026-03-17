"use client";

import { cn } from "@/lib/utils";

type FilterChipOption<TValue extends string> = {
  value: TValue;
  label: string;
};

type FilterChipGroupProps<TValue extends string> = {
  options: readonly FilterChipOption<TValue>[];
  value: TValue;
  onValueChange: (value: TValue) => void;
  className?: string;
};

export function FilterChipGroup<TValue extends string>({
  options,
  value,
  onValueChange,
  className,
}: FilterChipGroupProps<TValue>) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      {options.map((option) => {
        const active = option.value === value;

        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onValueChange(option.value)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-sm font-medium transition-colors",
              active
                ? "border-primary/35 bg-primary/12 text-foreground"
                : "border-border/70 bg-background/45 text-muted-foreground hover:bg-muted/70"
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
