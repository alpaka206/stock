import { NextRequest, NextResponse } from "next/server";

import { buildBackendMutationHeaders } from "@/lib/server/backend-csrf";
import { buildBackendUrl } from "@/lib/server/backend-url";

export async function POST(request: NextRequest) {
  const targetUrl = buildBackendUrl("/auth/dev-login");
  const response = await fetch(targetUrl, {
    method: "POST",
    headers: await buildBackendMutationHeaders(targetUrl, request.headers.get("cookie")),
    body: await request.text(),
    cache: "no-store",
  });

  return copyBackendResponse(response);
}

function copyBackendResponse(response: Response) {
  const nextResponse = new NextResponse(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
  copySetCookie(response, nextResponse);
  return nextResponse;
}

function copySetCookie(response: Response, nextResponse: NextResponse) {
  response.headers
    .get("set-cookie")
    ?.split(/,(?=\s*[^;]+=)/)
    .forEach((cookie) => nextResponse.headers.append("Set-Cookie", cookie.trim()));
}
