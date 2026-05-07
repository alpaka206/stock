import { NextRequest, NextResponse } from "next/server";

import type {
  ResearchSnapshot,
  ResearchSnapshotListResponse,
  ResearchSnapshotMutationResponse,
} from "@/lib/research/types";

const SNAPSHOT_API_TIMEOUT_MS = 5000;

type SnapshotListResponse = ResearchSnapshotListResponse & {
  status?: "success" | "disabled" | "error";
  errorMessage?: string;
};

type SnapshotMutationResponse = ResearchSnapshotMutationResponse & {
  status?: "success" | "disabled" | "error";
  errorMessage?: string;
};

export async function GET(request: NextRequest) {
  const apiUrl = resolveSnapshotApiUrl();

  if (!apiUrl) {
    return NextResponse.json({
      snapshots: [],
      status: "disabled",
    } satisfies SnapshotListResponse);
  }

  const url = new URL(apiUrl);
  const symbol = request.nextUrl.searchParams.get("symbol");
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
        snapshots: [],
        status: "error",
        errorMessage: `snapshot API responded with ${response.status}`,
      } satisfies SnapshotListResponse);
    }

    const payload = (await response.json()) as SnapshotListResponse;
    return NextResponse.json({ ...payload, status: "success" });
  } catch (error) {
    return NextResponse.json({
      snapshots: [],
      status: "error",
      errorMessage: error instanceof Error ? error.message : "snapshot API failed",
    } satisfies SnapshotListResponse);
  }
}

export async function POST(request: NextRequest) {
  const snapshot = (await request.json()) as ResearchSnapshot;
  const apiUrl = resolveSnapshotApiUrl();

  if (!apiUrl) {
    return NextResponse.json(
      { snapshot, status: "disabled" } satisfies SnapshotMutationResponse,
      { status: 202 }
    );
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
      return NextResponse.json(
        {
          snapshot,
          status: "error",
          errorMessage: `snapshot API responded with ${response.status}`,
        } satisfies SnapshotMutationResponse,
        { status: 202 }
      );
    }

    const payload = (await response.json()) as SnapshotMutationResponse;
    return NextResponse.json({ ...payload, status: "success" });
  } catch (error) {
    return NextResponse.json(
      {
        snapshot,
        status: "error",
        errorMessage: error instanceof Error ? error.message : "snapshot API failed",
      } satisfies SnapshotMutationResponse,
      { status: 202 }
    );
  }
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
