"use client";

import * as React from "react";

import { useStoredState } from "@/lib/client/use-stored-state";
import type {
  ResearchSnapshot,
  ResearchSnapshotConviction,
  ResearchSnapshotListResponse,
  ResearchSnapshotMutationResponse,
  ResearchSnapshotStance,
} from "@/lib/research/types";

const MAX_RESEARCH_SNAPSHOTS = 120;
const DEFAULT_STORAGE_KEY = "stock-workspace:research-snapshots";
const SNAPSHOT_API_PATH = "/api/research-snapshots";

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

type SnapshotSyncStatus = "idle" | "loading" | "ready" | "error";

type SnapshotListApiResponse = Partial<ResearchSnapshotListResponse> & {
  status?: "success" | "disabled" | "error";
};

type SnapshotMutationApiResponse = Partial<ResearchSnapshotMutationResponse> & {
  status?: "success" | "disabled" | "error";
};

export function useResearchSnapshots(storageKey = DEFAULT_STORAGE_KEY) {
  const { hasLoaded, value, setValue } = useStoredState<ResearchSnapshot[]>(
    storageKey,
    []
  );
  const [snapshotSyncStatus, setSnapshotSyncStatus] =
    React.useState<SnapshotSyncStatus>("idle");

  const snapshots = React.useMemo(
    () => [...value].sort((left, right) => right.createdAt.localeCompare(left.createdAt)),
    [value]
  );

  React.useEffect(() => {
    if (!hasLoaded) {
      return;
    }

    let cancelled = false;
    setSnapshotSyncStatus("loading");

    fetch(SNAPSHOT_API_PATH, {
      headers: {
        Accept: "application/json",
      },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`snapshot sync failed with ${response.status}`);
        }

        return (await response.json()) as SnapshotListApiResponse;
      })
      .then((payload) => {
        if (cancelled) {
          return;
        }

        if (Array.isArray(payload.snapshots)) {
          setValue((currentSnapshots) =>
            mergeSnapshots(payload.snapshots ?? [], currentSnapshots)
          );
        }

        setSnapshotSyncStatus(payload.status === "error" ? "error" : "ready");
      })
      .catch(() => {
        if (!cancelled) {
          setSnapshotSyncStatus("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [hasLoaded, setValue]);

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
      void persistSnapshot(nextSnapshot, setValue, setSnapshotSyncStatus);

      return nextSnapshot;
    },
    [setValue]
  );

  const removeSnapshot = React.useCallback(
    (snapshotId: string) => {
      setValue((currentSnapshots) =>
        currentSnapshots.filter((snapshot) => snapshot.id !== snapshotId)
      );
      void deletePersistedSnapshot(snapshotId, setSnapshotSyncStatus);
    },
    [setValue]
  );

  return {
    hasLoaded,
    snapshots,
    snapshotSyncStatus,
    saveSnapshot,
    removeSnapshot,
  };
}

function mergeSnapshots(
  primarySnapshots: ResearchSnapshot[],
  secondarySnapshots: ResearchSnapshot[]
) {
  const snapshotById = new Map<string, ResearchSnapshot>();

  [...secondarySnapshots, ...primarySnapshots].forEach((snapshot) => {
    snapshotById.set(snapshot.id, snapshot);
  });

  return Array.from(snapshotById.values())
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, MAX_RESEARCH_SNAPSHOTS);
}

async function persistSnapshot(
  snapshot: ResearchSnapshot,
  setValue: React.Dispatch<React.SetStateAction<ResearchSnapshot[]>>,
  setSnapshotSyncStatus: React.Dispatch<React.SetStateAction<SnapshotSyncStatus>>
) {
  try {
    const response = await fetch(SNAPSHOT_API_PATH, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(snapshot),
    });

    if (!response.ok) {
      throw new Error(`snapshot persist failed with ${response.status}`);
    }

    const payload = (await response.json()) as SnapshotMutationApiResponse;
    if (payload.snapshot) {
      setValue((currentSnapshots) => mergeSnapshots([payload.snapshot!], currentSnapshots));
    }

    setSnapshotSyncStatus(payload.status === "error" ? "error" : "ready");
  } catch {
    setSnapshotSyncStatus("error");
  }
}

async function deletePersistedSnapshot(
  snapshotId: string,
  setSnapshotSyncStatus: React.Dispatch<React.SetStateAction<SnapshotSyncStatus>>
) {
  try {
    const response = await fetch(
      `${SNAPSHOT_API_PATH}/${encodeURIComponent(snapshotId)}`,
      {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`snapshot delete failed with ${response.status}`);
    }

    const payload = (await response.json()) as { status?: "success" | "disabled" | "error" };
    setSnapshotSyncStatus(payload.status === "error" ? "error" : "ready");
  } catch {
    setSnapshotSyncStatus("error");
  }
}
