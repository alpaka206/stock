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
  const [suggestions, setSuggestions] = React.useState<InstrumentCatalogItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const deferredQuery = React.useDeferredValue(query.trim());

  React.useEffect(() => {
    setQuery(selectedSymbol);
  }, [selectedSymbol]);

  React.useEffect(() => {
    if (!deferredQuery) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    const controller = new AbortController();
    const timeoutId = window.setTimeout(async () => {
      setIsLoading(true);
      const fallbackItems = filterInstruments(deferredQuery).slice(0, 6);

      try {
        const response = await fetch(
          `/api/instruments/search?q=${encodeURIComponent(deferredQuery)}&limit=6`,
          {
            method: "GET",
            cache: "no-store",
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`instrument search failed: ${response.status}`);
        }

        const payload = (await response.json()) as {
          items?: InstrumentCatalogItem[];
        };
        const items = Array.isArray(payload.items) ? payload.items : [];
        setSuggestions(mergeUniqueInstruments(items, fallbackItems).slice(0, 6));
      } catch (error) {
        if ((error as Error).name === "AbortError") {
          return;
        }
        setSuggestions(fallbackItems);
      } finally {
        setIsLoading(false);
      }
    }, 180);

    return () => {
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [deferredQuery]);

  const quickInstrumentMap = React.useMemo(() => {
    const merged = mergeUniqueInstruments(
      suggestions,
      quickSymbols.flatMap((symbol) => filterInstruments(symbol))
    );
    return new Map(
      merged.map((instrument) => [instrument.symbol.trim().toUpperCase(), instrument])
    );
  }, [quickSymbols, suggestions]);

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
            onClick={() => onSelect(resolveQuickInstrument(symbol, quickInstrumentMap))}
          >
            {symbol}
          </Button>
        ))}
      </div>
      {helperText ? (
        <p className="text-sm leading-6 text-muted-foreground">{helperText}</p>
      ) : null}
      {deferredQuery ? (
        <p className="text-xs text-muted-foreground">
          {isLoading ? "실시간 검색 결과를 불러오는 중입니다." : "미국/한국 종목을 통합 검색합니다."}
        </p>
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

function mergeUniqueInstruments(
  primary: InstrumentCatalogItem[],
  secondary: InstrumentCatalogItem[]
) {
  const merged: InstrumentCatalogItem[] = [];
  const seenSymbols = new Set<string>();

  for (const instrument of [...primary, ...secondary]) {
    const symbol = instrument.symbol.trim().toUpperCase();

    if (!symbol || seenSymbols.has(symbol)) {
      continue;
    }

    seenSymbols.add(symbol);
    merged.push(instrument);
  }

  return merged;
}

function resolveQuickInstrument(
  symbol: string,
  quickInstrumentMap: Map<string, InstrumentCatalogItem>
): InstrumentCatalogItem {
  const normalizedSymbol = symbol.trim().toUpperCase();
  const matched =
    quickInstrumentMap.get(normalizedSymbol) ??
    filterInstruments(symbol).find(
      (instrument) => instrument.symbol.trim().toUpperCase() === normalizedSymbol
    );

  if (matched) {
    return matched;
  }

  const securityCode = normalizedSymbol.split(".", 1)[0] ?? normalizedSymbol;
  const exchange = normalizedSymbol.endsWith(".KS")
    ? "KRX"
    : normalizedSymbol.endsWith(".KQ")
      ? "KOSDAQ"
      : "";

  return {
    symbol,
    name: symbol,
    securityCode,
    aliases: [],
    exchange,
    sector: "",
  };
}
