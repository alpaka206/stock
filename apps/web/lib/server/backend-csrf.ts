import "server-only";

type CsrfTokenResponse = {
  headerName?: string;
  token?: string;
};

export async function buildBackendMutationHeaders(apiUrl: string) {
  const headers = new Headers({
    Accept: "application/json",
    "Content-Type": "application/json",
  });
  const csrf = await fetchBackendCsrf(apiUrl);

  if (csrf) {
    headers.set(csrf.headerName, csrf.token);
    headers.set("Cookie", csrf.cookieHeader);
  }

  return headers;
}

async function fetchBackendCsrf(apiUrl: string) {
  try {
    const response = await fetch(resolveCsrfUrl(apiUrl), {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal:
        typeof AbortSignal.timeout === "function"
          ? AbortSignal.timeout(5000)
          : undefined,
    });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as CsrfTokenResponse;
    if (!payload.headerName || !payload.token) {
      return null;
    }

    return {
      headerName: payload.headerName,
      token: payload.token,
      cookieHeader: resolveCookieHeader(response.headers, payload.token),
    };
  } catch {
    return null;
  }
}

function resolveCsrfUrl(apiUrl: string) {
  const baseUrl = process.env.STOCK_API_BASE_URL?.trim();
  if (baseUrl) {
    return `${baseUrl.replace(/\/$/, "")}/csrf`;
  }

  return `${new URL(apiUrl).origin}/csrf`;
}

function resolveCookieHeader(headers: Headers, token: string) {
  const rawSetCookie = headers.get("set-cookie");
  if (!rawSetCookie) {
    return `XSRF-TOKEN=${token}`;
  }

  const cookies = rawSetCookie
    .split(/,(?=\s*[^;]+=)/)
    .map((cookie) => cookie.split(";", 1)[0]?.trim())
    .filter(Boolean);

  return cookies.length > 0 ? cookies.join("; ") : `XSRF-TOKEN=${token}`;
}
