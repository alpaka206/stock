"use client";

import * as React from "react";
import { Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { filterInstruments } from "@/dev/fixtures/instruments";
import type { InstrumentCatalogItem } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type InstrumentSearchProps = {
  selectedSymbol: string;
  label?: string;
  helperText?: string;
  quickSymbols?: string[];
  className?: string;
  onSelect: (instrument: InstrumentCatalogItem) => void;
};

export function InstrumentSearch({
  selectedSymbol,
  label = "종목 검색",
  helperText,
  quickSymbols = [],
  className,
  onSelect,
}: InstrumentSearchProps) {
  const [query, setQuery] = React.useState(selectedSymbol);

  React.useEffect(() => {
    setQuery(selectedSymbol);
  }, [selectedSymbol]);

  const suggestions = React.useMemo(() => {
    if (!query.trim()) {
      return [];
    }

    return filterInstruments(query).slice(0, 6);
  }, [query]);

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center gap-2 rounded-[calc(var(--radius)*1.05)] border border-border/60 bg-background/55 px-3 py-2">
        <Search className="size-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="티커, 종목명, 종목번호로 찾기"
          className="border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
        />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          {label}
        </span>
        {quickSymbols.map((symbol) => (
          <Button
            key={symbol}
            type="button"
            size="sm"
            variant={symbol === selectedSymbol ? "default" : "outline"}
            onClick={() => {
              const instrument = filterInstruments(symbol)[0];
              if (instrument) {
                onSelect(instrument);
              }
            }}
          >
            {symbol}
          </Button>
        ))}
      </div>
      {helperText ? (
        <p className="text-sm leading-6 text-muted-foreground">{helperText}</p>
      ) : null}
      {suggestions.length > 0 ? (
        <div className="grid gap-2 md:grid-cols-2">
          {suggestions.map((instrument) => (
            <button
              key={`${instrument.symbol}-${instrument.securityCode}`}
              type="button"
              onClick={() => onSelect(instrument)}
              className={cn(
                "rounded-[calc(var(--radius)*1.05)] border px-3 py-3 text-left transition-colors",
                instrument.symbol === selectedSymbol
                  ? "border-primary/35 bg-primary/10"
                  : "border-border/60 bg-background/25 hover:bg-muted/60"
              )}
            >
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold tracking-tight">
                  {instrument.symbol}
                </p>
                <span className="numeric text-xs text-muted-foreground">
                  {instrument.securityCode}
                </span>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{instrument.name}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                {instrument.sector ?? "섹터 미분류"}
              </p>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
