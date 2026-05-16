import { NextRequest, NextResponse } from "next/server";

import { buildBackendMutationHeaders } from "@/lib/server/backend-csrf";
import { buildBackendUrl } from "@/lib/server/backend-url";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context, "GET");
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context, "POST");
}

async function proxyBackend(
  request: NextRequest,
  context: RouteContext,
  method: "GET" | "POST"
) {
  const path = (await context.params).path.join("/");
  if (!isAllowedPlatformPath(path)) {
    return NextResponse.json({ message: "허용되지 않은 workspace API 경로입니다." }, { status: 404 });
  }

  const targetUrl = new URL(buildBackendUrl(`/${path}`));
  const incomingUrl = new URL(request.url);
  targetUrl.search = incomingUrl.search;

  const headers =
    method === "POST"
      ? await buildBackendMutationHeaders(targetUrl.toString(), request.headers.get("cookie"))
      : new Headers({
          Accept: "application/json",
          Cookie: request.headers.get("cookie") ?? "",
        });

  const response = await fetch(targetUrl, {
    method,
    headers,
    body: method === "POST" ? await request.text() : undefined,
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

function isAllowedPlatformPath(path: string) {
  return (
    [
      "subscription-plans",
      "report-schedules",
      "media-assets",
      "localization-jobs",
      "reports",
      "reports/preview",
      "reports/send",
    ].includes(path) ||
    /^localization-jobs\/[0-9a-fA-F-]+\/(submit|sync)$/.test(path)
  );
}
