"use client";

import * as React from "react";

import type {
  ResearchSnapshot,
  ResearchSnapshotConviction,
  ResearchSnapshotListResponse,
  ResearchSnapshotMutationResponse,
  ResearchSnapshotStance,
} from "@/lib/research/types";

const MAX_RESEARCH_SNAPSHOTS = 120;
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
  status?: "success" | "local" | "error";
};

type SnapshotMutationApiResponse = Partial<ResearchSnapshotMutationResponse> & {
  status?: "success" | "local" | "error";
};

export function useResearchSnapshots() {
  const [hasLoaded, setHasLoaded] = React.useState(false);
  const [snapshots, setSnapshots] = React.useState<ResearchSnapshot[]>([]);
  const [snapshotSyncStatus, setSnapshotSyncStatus] =
    React.useState<SnapshotSyncStatus>("idle");

  React.useEffect(() => {
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

        setSnapshots(normalizeSnapshots(payload.snapshots ?? []));
        setHasLoaded(true);
        setSnapshotSyncStatus(payload.status === "error" ? "error" : "ready");
      })
      .catch(() => {
        if (!cancelled) {
          setHasLoaded(true);
          setSnapshotSyncStatus("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const saveSnapshot = React.useCallback((input: SaveResearchSnapshotInput) => {
    const optimisticSnapshot: ResearchSnapshot = {
      ...input,
      id: `pending-${Date.now()}`,
      createdAt: input.createdAt ?? new Date().toISOString(),
    };

    setSnapshots((currentSnapshots) =>
      normalizeSnapshots([optimisticSnapshot, ...currentSnapshots])
    );
    void persistSnapshot(input, setSnapshots, setSnapshotSyncStatus);

    return optimisticSnapshot;
  }, []);

  const removeSnapshot = React.useCallback((snapshotId: string) => {
    setSnapshots((currentSnapshots) =>
      currentSnapshots.filter((snapshot) => snapshot.id !== snapshotId)
    );
    void deletePersistedSnapshot(snapshotId, setSnapshotSyncStatus);
  }, []);

  return {
    hasLoaded,
    snapshots,
    snapshotSyncStatus,
    saveSnapshot,
    removeSnapshot,
  };
}

function normalizeSnapshots(items: ResearchSnapshot[]) {
  const snapshotById = new Map<string, ResearchSnapshot>();

  items.forEach((snapshot) => {
    snapshotById.set(snapshot.id, snapshot);
  });

  return Array.from(snapshotById.values())
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, MAX_RESEARCH_SNAPSHOTS);
}

async function persistSnapshot(
  snapshot: SaveResearchSnapshotInput,
  setSnapshots: React.Dispatch<React.SetStateAction<ResearchSnapshot[]>>,
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
      setSnapshots((currentSnapshots) =>
        normalizeSnapshots([
          payload.snapshot!,
          ...currentSnapshots.filter((item) => !item.id.startsWith("pending-")),
        ])
      );
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

    const payload = (await response.json()) as { status?: "success" | "local" | "error" };
    setSnapshotSyncStatus(payload.status === "error" ? "error" : "ready");
  } catch {
    setSnapshotSyncStatus("error");
  }
}
