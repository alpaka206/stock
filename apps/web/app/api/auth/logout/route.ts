import { NextRequest, NextResponse } from "next/server";

import { buildBackendMutationHeaders } from "@/lib/server/backend-csrf";
import { buildBackendUrl } from "@/lib/server/backend-url";

export async function POST(request: NextRequest) {
  const targetUrl = buildBackendUrl("/auth/logout");
  const response = await fetch(targetUrl, {
    method: "POST",
    headers: await buildBackendMutationHeaders(targetUrl, request.headers.get("cookie")),
    body: "{}",
    cache: "no-store",
  });

  const nextResponse = new NextResponse(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
  response.headers
    .get("set-cookie")
    ?.split(/,(?=\s*[^;]+=)/)
    .forEach((cookie) => nextResponse.headers.append("Set-Cookie", cookie.trim()));
  return nextResponse;
}
