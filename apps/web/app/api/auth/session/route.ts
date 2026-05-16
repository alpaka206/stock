import { headers } from "next/headers";
import { NextResponse } from "next/server";

import { buildBackendUrl } from "@/lib/server/backend-url";

export async function GET() {
  const requestHeaders = await headers();
  const response = await fetch(buildBackendUrl("/auth/me"), {
    cache: "no-store",
    headers: {
      Accept: "application/json",
      Cookie: requestHeaders.get("cookie") ?? "",
    },
  });

  return new NextResponse(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
}
