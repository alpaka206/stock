import { NextRequest, NextResponse } from "next/server";

import type {
  ResearchSnapshot,
  ResearchSnapshotListResponse,
  ResearchSnapshotMutationResponse,
} from "@/lib/research/types";

const SNAPSHOT_API_TIMEOUT_MS = 5000;

type SnapshotListResponse = ResearchSnapshotListResponse & {
  status?: "success" | "local" | "error";
  errorMessage?: string;
};

type SnapshotMutationResponse = ResearchSnapshotMutationResponse & {
  status?: "success" | "local" | "error";
  errorMessage?: string;
};

export async function GET(request: NextRequest) {
  const apiUrl = resolveSnapshotApiUrl();
  const symbol = request.nextUrl.searchParams.get("symbol");

  if (!apiUrl) {
    return NextResponse.json({
      snapshots: await listLocalSnapshots(symbol),
      status: "local",
    } satisfies SnapshotListResponse);
  }

  const url = new URL(apiUrl);
  if (symbol) {
    url.searchParams.set("symbol", symbol);
  }

  try {
    const response = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: buildTimeoutSignal(),
    });

    if (!response.ok) {
      return NextResponse.json({
        snapshots: await listLocalSnapshots(symbol),
        status: "local",
        errorMessage: `snapshot API responded with ${response.status}`,
      } satisfies SnapshotListResponse);
    }

    const payload = (await response.json()) as SnapshotListResponse;
    return NextResponse.json({ ...payload, status: "success" });
  } catch (error) {
    return NextResponse.json({
      snapshots: await listLocalSnapshots(symbol),
      status: "local",
      errorMessage: error instanceof Error ? error.message : "snapshot API failed",
    } satisfies SnapshotListResponse);
  }
}

export async function POST(request: NextRequest) {
  const snapshot = (await request.json()) as Omit<ResearchSnapshot, "id" | "createdAt"> &
    Partial<Pick<ResearchSnapshot, "id" | "createdAt">>;
  const apiUrl = resolveSnapshotApiUrl();

  if (!apiUrl) {
    return NextResponse.json({
      snapshot: await saveLocalSnapshot(snapshot),
      status: "local",
    } satisfies SnapshotMutationResponse);
  }

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(snapshot),
      signal: buildTimeoutSignal(),
    });

    if (!response.ok) {
      return NextResponse.json({
        snapshot: await saveLocalSnapshot(snapshot),
        status: "local",
        errorMessage: `snapshot API responded with ${response.status}`,
      } satisfies SnapshotMutationResponse);
    }

    const payload = (await response.json()) as SnapshotMutationResponse;
    return NextResponse.json({ ...payload, status: "success" });
  } catch (error) {
    return NextResponse.json({
      snapshot: await saveLocalSnapshot(snapshot),
      status: "local",
      errorMessage: error instanceof Error ? error.message : "snapshot API failed",
    } satisfies SnapshotMutationResponse);
  }
}

async function listLocalSnapshots(symbol: string | null) {
  const { listServerSnapshots } = await import("@/lib/server/snapshot-store");
  return listServerSnapshots(symbol);
}

async function saveLocalSnapshot(
  snapshot: Omit<ResearchSnapshot, "id" | "createdAt"> &
    Partial<Pick<ResearchSnapshot, "id" | "createdAt">>
) {
  const { saveServerSnapshot } = await import("@/lib/server/snapshot-store");
  return saveServerSnapshot(snapshot);
}

function resolveSnapshotApiUrl() {
  const explicitUrl = process.env.SNAPSHOT_API_URL?.trim();
  if (explicitUrl) {
    return explicitUrl.replace(/\/$/, "");
  }

  const baseUrl = process.env.STOCK_API_BASE_URL?.trim();
  if (!baseUrl) {
    return null;
  }

  return `${baseUrl.replace(/\/$/, "")}/snapshots`;
}

function buildTimeoutSignal() {
  return typeof AbortSignal.timeout === "function"
    ? AbortSignal.timeout(SNAPSHOT_API_TIMEOUT_MS)
    : undefined;
}
