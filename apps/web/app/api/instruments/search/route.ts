import { NextRequest, NextResponse } from "next/server";

import { filterInstruments } from "@/dev/fixtures/instruments";
import { fetchResearchApiJson } from "@/lib/server/research-api";
import type { InstrumentCatalogItem } from "@/lib/research/types";

type InstrumentSearchApiResponse = {
  items: InstrumentCatalogItem[];
};

type RemoteInstrumentSearchApiResponse = {
  items: RemoteInstrumentCatalogItem[];
};

type RemoteInstrumentCatalogItem = Partial<InstrumentCatalogItem> & {
  symbol: string;
  name?: string;
  displayName?: string;
  securityCode?: string;
  market?: string;
};

const DEFAULT_LIMIT = 6;
const MAX_LIMIT = 10;
const SEARCH_TIMEOUT_MS = 8000;

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  const requestedLimit = Number.parseInt(
    request.nextUrl.searchParams.get("limit") ?? String(DEFAULT_LIMIT),
    10
  );
  const limit = Number.isFinite(requestedLimit)
    ? Math.min(Math.max(requestedLimit, 1), MAX_LIMIT)
    : DEFAULT_LIMIT;

  if (!query) {
    return NextResponse.json<InstrumentSearchApiResponse>({ items: [] });
  }

  const fallbackItems = filterInstruments(query).slice(0, limit);
  const result = await fetchResearchApiJson<RemoteInstrumentSearchApiResponse>({
    explicitUrlEnv: "INSTRUMENT_SEARCH_API_URL",
    basePath: "instruments/search",
    query: {
      q: query,
      limit: String(limit),
    },
    timeoutMs: 8000,
  });

  if (result.status === "success" && result.payload.items.length > 0) {
    return NextResponse.json<InstrumentSearchApiResponse>({
      items: mergeUniqueInstruments(
        normalizeRemoteInstruments(result.payload.items),
        fallbackItems
      ).slice(0, limit),
    });
  }

  const yahooItems = await searchYahooInstruments(query, limit);
  return NextResponse.json<InstrumentSearchApiResponse>({
    items: mergeUniqueInstruments(yahooItems, fallbackItems).slice(0, limit),
  });
}

function normalizeRemoteInstruments(items: RemoteInstrumentCatalogItem[]) {
  const normalized: InstrumentCatalogItem[] = [];

  for (const item of items) {
    const symbol = String(item.symbol ?? "")
      .trim()
      .toUpperCase();
    if (!symbol) {
      continue;
    }

    const name = String(item.name ?? item.displayName ?? symbol).trim();
    const aliases = Array.isArray(item.aliases)
      ? item.aliases.map((alias) => String(alias).trim()).filter(Boolean)
      : [];

    normalized.push({
      symbol,
      name,
      securityCode: String(item.securityCode ?? symbol.split(".", 1)[0] ?? symbol).trim(),
      aliases,
      sector: item.sector ? String(item.sector).trim() : undefined,
      exchange: item.exchange || item.market ? String(item.exchange ?? item.market).trim() : undefined,
    });
  }

  return normalized;
}

function mergeUniqueInstruments(
  primary: InstrumentCatalogItem[],
  secondary: InstrumentCatalogItem[]
) {
  const merged: InstrumentCatalogItem[] = [];
  const seenSymbols = new Set<string>();

  for (const instrument of [...primary, ...secondary]) {
    const symbol = instrument.symbol.trim().toUpperCase();

    if (!symbol || seenSymbols.has(symbol)) {
      continue;
    }

    seenSymbols.add(symbol);
    merged.push(instrument);
  }

  return merged;
}

async function searchYahooInstruments(query: string, limit: number) {
  try {
    const items = await fetchYahooSearch(query, limit);
    if (items.length > 0) {
      return items;
    }

    if (/^\d{6}$/.test(query.trim())) {
      const domesticCandidates = await Promise.all(
        [".KS", ".KQ"].map((suffix) => fetchYahooSearch(`${query.trim()}${suffix}`, 1))
      );
      return mergeUniqueInstruments(domesticCandidates.flat(), []);
    }
  } catch {
    return [];
  }

  return [];
}

async function fetchYahooSearch(query: string, limit: number) {
  const url = new URL("https://query1.finance.yahoo.com/v1/finance/search");
  url.searchParams.set("q", query);
  url.searchParams.set("quotesCount", String(Math.max(limit * 4, 12)));
  url.searchParams.set("newsCount", "0");
  url.searchParams.set("enableFuzzyQuery", "true");

  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      "User-Agent": "Mozilla/5.0",
    },
    cache: "no-store",
    signal:
      typeof AbortSignal.timeout === "function"
        ? AbortSignal.timeout(SEARCH_TIMEOUT_MS)
        : undefined,
  });

  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as {
    quotes?: Array<Record<string, unknown>>;
  };
  const quotes = Array.isArray(payload.quotes) ? payload.quotes : [];
  const items: InstrumentCatalogItem[] = [];
  const seenSymbols = new Set<string>();

  for (const quote of quotes) {
    const symbol = String(quote.symbol ?? "")
      .trim()
      .toUpperCase();
    const quoteType = String(quote.quoteType ?? "")
      .trim()
      .toUpperCase();

    if (!symbol || quoteType !== "EQUITY" || seenSymbols.has(symbol)) {
      continue;
    }

    seenSymbols.add(symbol);
    items.push({
      symbol,
      name: String(quote.longname ?? quote.shortname ?? symbol).trim(),
      securityCode: symbol.split(".", 1)[0] ?? symbol,
      aliases: buildAliases(quote),
      sector: mapSector(
        String(
          quote.industryDisp ??
            quote.industry ??
            quote.sectorDisp ??
            quote.sector ??
            ""
        )
      ),
      exchange: String(quote.exchDisp ?? quote.exchange ?? "").trim(),
    });

    if (items.length >= limit) {
      break;
    }
  }

  return items;
}

function buildAliases(quote: Record<string, unknown>) {
  const aliases: string[] = [];
  for (const candidate of [
    quote.shortname,
    quote.longname,
    quote.symbol,
    quote.exchange,
    quote.exchDisp,
  ]) {
    const text = String(candidate ?? "").trim();
    if (text && !aliases.includes(text)) {
      aliases.push(text);
    }
  }
  return aliases;
}

function mapSector(value: string) {
  const normalized = value.trim().toLowerCase();
  if (normalized.includes("semiconductor")) {
    return "반도체";
  }
  if (normalized.includes("software")) {
    return "소프트웨어";
  }
  if (normalized.includes("security")) {
    return "사이버보안";
  }
  if (normalized.includes("power") || normalized.includes("utility")) {
    return "전력 인프라";
  }
  if (normalized.includes("technology")) {
    return "기술주";
  }
  return value.trim();
}
