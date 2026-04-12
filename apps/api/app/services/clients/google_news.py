from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
import re
from typing import Any
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

import httpx

from app.services.errors import ExternalServiceError


GLOBAL_NEWS_QUERIES = (
    "US stock market OR Nasdaq OR S&P 500 when:2d",
    "earnings season Wall Street when:2d",
)

NOISE_TITLE_PATTERNS = (
    "stock quote",
    "price and forecast",
    "stock price and quote",
    "earnings history",
    "forecast |",
    "chart |",
    "futures and options",
    "new york stock exchange",
    "quote -",
    "nasdaq:",
)


class GoogleNewsClient:
    def __init__(self, *, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://news.google.com/rss/search"
        self.base_params = {
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        }
        self.base_headers = {"User-Agent": "Mozilla/5.0"}

    async def get_market_headlines(self, *, limit: int = 8) -> list[dict[str, Any]]:
        articles = await self._collect_queries(
            queries=[(query, []) for query in GLOBAL_NEWS_QUERIES],
            limit=limit,
        )
        if not articles:
            raise ExternalServiceError("Google News RSS market headlines are unavailable.")
        return articles

    async def get_watchlist_headlines(
        self, *, tickers: list[str], limit: int = 8
    ) -> list[dict[str, Any]]:
        queries = [
            (f"{symbol} stock earnings OR guidance when:7d", [symbol])
            for symbol in tickers[:5]
        ]
        articles = await self._collect_queries(queries=queries, limit=limit)
        if not articles:
            raise ExternalServiceError("Google News RSS watchlist headlines are unavailable.")
        return articles

    async def _collect_queries(
        self, *, queries: list[tuple[str, list[str]]], limit: int
    ) -> list[dict[str, Any]]:
        seen_titles: set[str] = set()
        collected: list[dict[str, Any]] = []

        for query, tickers in queries:
            items = await self._fetch_query(query)
            for item in items:
                normalized_title = item["title"].strip().lower()
                if not normalized_title or normalized_title in seen_titles:
                    continue
                if not self._is_article_candidate(item["title"], item["source"]):
                    continue
                seen_titles.add(normalized_title)
                collected.append(
                    {
                        "id_seed": item["guid"] or item["link"] or item["title"],
                        "title": item["title"],
                        "summary": f'{item["source"]} 기사 제목 기준입니다. 원문에서 세부 내용을 확인하세요.',
                        "source": item["source"] or "Google News RSS",
                        "url": item["link"],
                        "publishedAt": item["publishedAt"],
                        "sentimentScore": 0.0,
                        "sentimentLabel": "Neutral",
                        "tickers": tickers,
                        "sourceKey": "google_news::rss_search",
                    }
                )
                if len(collected) >= limit:
                    return collected

        return collected

    async def _fetch_query(self, query: str) -> list[dict[str, str]]:
        params = {**self.base_params, "q": query}
        url = f"{self.base_url}?{urlencode(params)}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, headers=self.base_headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.text
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"Google News RSS search failed with HTTP {exc.response.status_code}."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Google News RSS search timed out.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("Google News RSS search failed with a network error.") from exc

        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise ExternalServiceError("Google News RSS returned invalid XML.") from exc

        items: list[dict[str, str]] = []
        for item in root.findall(".//item"):
            raw_title = (item.findtext("title") or "").strip()
            title, derived_source = self._split_title_and_source(raw_title)
            source = (item.findtext("source") or derived_source or "Google News RSS").strip()
            items.append(
                {
                    "guid": (item.findtext("guid") or "").strip(),
                    "title": title,
                    "source": source,
                    "link": (item.findtext("link") or "").strip(),
                    "publishedAt": self._format_pub_date(item.findtext("pubDate") or ""),
                }
            )
        return items

    def _split_title_and_source(self, raw_title: str) -> tuple[str, str]:
        parts = [part.strip() for part in raw_title.rsplit(" - ", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]
        return raw_title, ""

    def _is_article_candidate(self, title: str, source: str) -> bool:
        normalized = unescape(f"{title} {source}").strip().lower()
        if not normalized:
            return False
        return not any(pattern in normalized for pattern in NOISE_TITLE_PATTERNS)

    def _format_pub_date(self, value: str) -> str:
        if not value:
            return datetime.now(timezone.utc).isoformat()
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError, IndexError):
            pass

        cleaned = re.sub(r"\s+", " ", value).strip()
        if cleaned:
            try:
                parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc).isoformat()
            except ValueError:
                pass

        return datetime.now(timezone.utc).isoformat()
