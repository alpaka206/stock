"use client";

import * as React from "react";

import { useStoredState } from "@/lib/client/use-stored-state";

const MAX_RECENT_SYMBOLS = 6;

export function useRecentSymbols(storageKey: string, initialSymbols: string[] = []) {
  const { hasLoaded, value, setValue } = useStoredState<string[]>(
    storageKey,
    initialSymbols
  );

  const symbols = React.useMemo(
    () => value.map((symbol) => symbol.toUpperCase()).slice(0, MAX_RECENT_SYMBOLS),
    [value]
  );

  const pushSymbol = React.useCallback(
    (symbol: string) => {
      const normalizedSymbol = symbol.trim().toUpperCase();

      if (!normalizedSymbol) {
        return;
      }

      setValue((currentSymbols) => {
        const normalizedCurrent = currentSymbols.map((item) => item.toUpperCase());
        const nextSymbols = [
          normalizedSymbol,
          ...normalizedCurrent.filter((item) => item !== normalizedSymbol),
        ].slice(0, MAX_RECENT_SYMBOLS);

        const isSame =
          nextSymbols.length === normalizedCurrent.length &&
          nextSymbols.every((item, index) => item === normalizedCurrent[index]);

        return isSame ? currentSymbols : nextSymbols;
      });
    },
    [setValue]
  );

  return {
    hasLoaded,
    symbols,
    pushSymbol,
  };
}
