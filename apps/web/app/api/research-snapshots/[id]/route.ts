import { NextRequest, NextResponse } from "next/server";

const SNAPSHOT_API_TIMEOUT_MS = 5000;

type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};

export async function DELETE(_request: NextRequest, context: RouteContext) {
  const { id } = await context.params;
  const apiUrl = resolveSnapshotApiUrl(id);

  if (!apiUrl) {
    return NextResponse.json({ deleted: false, id, status: "disabled" }, { status: 202 });
  }

  try {
    const response = await fetch(apiUrl, {
      method: "DELETE",
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: buildTimeoutSignal(),
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          deleted: false,
          id,
          status: "error",
          errorMessage: `snapshot API responded with ${response.status}`,
        },
        { status: 202 }
      );
    }

    const payload = (await response.json()) as { deleted: boolean; id: string };
    return NextResponse.json({ ...payload, status: "success" });
  } catch (error) {
    return NextResponse.json(
      {
        deleted: false,
        id,
        status: "error",
        errorMessage: error instanceof Error ? error.message : "snapshot API failed",
      },
      { status: 202 }
    );
  }
}

function resolveSnapshotApiUrl(id: string) {
  const explicitUrl = process.env.SNAPSHOT_API_URL?.trim();
  if (explicitUrl) {
    return `${explicitUrl.replace(/\/$/, "")}/${encodeURIComponent(id)}`;
  }

  const baseUrl = process.env.STOCK_API_BASE_URL?.trim();
  if (!baseUrl) {
    return null;
  }

  return `${baseUrl.replace(/\/$/, "")}/snapshots/${encodeURIComponent(id)}`;
}

function buildTimeoutSignal() {
  return typeof AbortSignal.timeout === "function"
    ? AbortSignal.timeout(SNAPSHOT_API_TIMEOUT_MS)
    : undefined;
}
