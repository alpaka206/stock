"use client";

import * as React from "react";

import { useStoredState } from "@/lib/client/use-stored-state";
import type {
  ResearchSnapshot,
  ResearchSnapshotConviction,
  ResearchSnapshotStance,
} from "@/lib/research/types";

const MAX_RESEARCH_SNAPSHOTS = 120;
const DEFAULT_STORAGE_KEY = "stock-workspace:research-snapshots";

export const researchSnapshotStanceTone: Record<
  ResearchSnapshotStance,
  "positive" | "negative" | "neutral"
> = {
  bullish: "positive",
  neutral: "neutral",
  bearish: "negative",
};

export const researchSnapshotConvictionValues: ResearchSnapshotConviction[] = [
  "low",
  "medium",
  "high",
];

export const researchSnapshotStanceValues: ResearchSnapshotStance[] = [
  "bullish",
  "neutral",
  "bearish",
];

type SaveResearchSnapshotInput = Omit<ResearchSnapshot, "id" | "createdAt"> & {
  createdAt?: string;
};

export function useResearchSnapshots(storageKey = DEFAULT_STORAGE_KEY) {
  const { hasLoaded, value, setValue } = useStoredState<ResearchSnapshot[]>(
    storageKey,
    []
  );

  const snapshots = React.useMemo(
    () => [...value].sort((left, right) => right.createdAt.localeCompare(left.createdAt)),
    [value]
  );

  const saveSnapshot = React.useCallback(
    (input: SaveResearchSnapshotInput) => {
      const nextSnapshot: ResearchSnapshot = {
        ...input,
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        createdAt: input.createdAt ?? new Date().toISOString(),
      };

      setValue((currentSnapshots) =>
        [nextSnapshot, ...currentSnapshots].slice(0, MAX_RESEARCH_SNAPSHOTS)
      );

      return nextSnapshot;
    },
    [setValue]
  );

  const removeSnapshot = React.useCallback(
    (snapshotId: string) => {
      setValue((currentSnapshots) =>
        currentSnapshots.filter((snapshot) => snapshot.id !== snapshotId)
      );
    },
    [setValue]
  );

  return {
    hasLoaded,
    snapshots,
    saveSnapshot,
    removeSnapshot,
  };
}
