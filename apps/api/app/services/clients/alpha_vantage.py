from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1
from typing import Any
import time

import httpx

from app.services.errors import (
    ExternalRateLimitError,
    ExternalServiceError,
    ProviderConfigurationError,
)


class AlphaVantageClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float,
        cache_ttl_seconds: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def get_daily_series(self, symbol: str, limit: int = 100) -> list[dict[str, Any]]:
        payload = await self._request(
            {"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "compact"}
        )
        raw_series = payload.get("Time Series (Daily)", {})
        if not raw_series:
            raise ExternalServiceError(f"{symbol} 일별 시계열 데이터를 찾지 못했습니다.")

        rows = [
            {
                "date": date,
                "open": float(row["1. open"]),
                "high": float(row["2. high"]),
                "low": float(row["3. low"]),
                "close": float(row["4. close"]),
                "volume": float(row["5. volume"]),
            }
            for date, row in sorted(raw_series.items(), reverse=True)
        ]
        return rows[:limit]

    async def get_company_overview(self, symbol: str) -> dict[str, Any]:
        payload = await self._request({"function": "OVERVIEW", "symbol": symbol})
        if not payload or "Symbol" not in payload:
            raise ExternalServiceError(f"{symbol} 기업 개요 데이터를 찾지 못했습니다.")

        return {
            "symbol": payload.get("Symbol", symbol),
            "name": payload.get("Name", symbol),
            "sector": payload.get("Sector", ""),
            "industry": payload.get("Industry", ""),
            "description": payload.get("Description", ""),
            "marketCapitalization": self._to_float(payload.get("MarketCapitalization")),
            "peratio": self._to_float(payload.get("PERatio")),
            "analystTargetPrice": self._to_float(payload.get("AnalystTargetPrice")),
        }

    async def get_news_sentiment(
        self,
        *,
        tickers: list[str] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"function": "NEWS_SENTIMENT", "limit": str(limit)}
        if tickers:
            params["tickers"] = ",".join(tickers)

        payload = await self._request(params)
        feed = payload.get("feed", [])
        if not feed:
            return []

        articles: list[dict[str, Any]] = []
        for item in feed[:limit]:
            articles.append(
                {
                    "id_seed": item.get("url") or item.get("title") or str(time.time()),
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "source": item.get("source", "Alpha Vantage"),
                    "url": item.get("url", ""),
                    "publishedAt": self._format_news_timestamp(item.get("time_published", "")),
                    "sentimentScore": self._to_float(item.get("overall_sentiment_score")),
                    "sentimentLabel": item.get("overall_sentiment_label", ""),
                    "tickers": [
                        ticker_item.get("ticker", "")
                        for ticker_item in item.get("ticker_sentiment", [])
                        if ticker_item.get("ticker")
                    ],
                }
            )
        return articles

    async def get_top_movers(self) -> dict[str, list[dict[str, Any]]]:
        payload = await self._request({"function": "TOP_GAINERS_LOSERS"})
        return {
            "topGainers": [self._parse_mover_row(row) for row in payload.get("top_gainers", [])[:3]],
            "topLosers": [self._parse_mover_row(row) for row in payload.get("top_losers", [])[:3]],
            "mostActivelyTraded": [
                self._parse_mover_row(row)
                for row in payload.get("most_actively_traded", [])[:3]
            ],
        }

    async def get_treasury_yield(
        self, *, maturity: str = "10year", interval: str = "daily"
    ) -> dict[str, Any]:
        payload = await self._request(
            {"function": "TREASURY_YIELD", "maturity": maturity, "interval": interval}
        )
        series = payload.get("data", [])
        if not series:
            raise ExternalServiceError("미국 국채 수익률 데이터를 찾지 못했습니다.")
        latest = series[0]
        return {"date": latest.get("date", ""), "value": self._to_float(latest.get("value"))}

    async def _request(self, params: dict[str, str]) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderConfigurationError(
                "real provider를 사용하려면 ALPHA_VANTAGE_API_KEY가 필요합니다."
            )

        merged = {**params, "apikey": self.api_key}
        cache_key = self._cache_key(merged)
        now = time.time()
        if cache_key in self._cache:
            expires_at, cached_payload = self._cache[cache_key]
            if expires_at > now:
                return cached_payload

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(self.base_url, params=merged)
            response.raise_for_status()
            payload = response.json()

        self._raise_for_provider_errors(payload)
        self._cache[cache_key] = (now + self.cache_ttl_seconds, payload)
        return payload

    def _raise_for_provider_errors(self, payload: dict[str, Any]) -> None:
        note = payload.get("Note") or payload.get("Information")
        if note:
            raise ExternalRateLimitError(str(note))

        if "Error Message" in payload:
            raise ExternalServiceError(str(payload["Error Message"]))

    def _cache_key(self, params: dict[str, str]) -> str:
        serialized = "&".join(f"{key}={params[key]}" for key in sorted(params))
        return sha1(serialized.encode("utf-8")).hexdigest()

    def _parse_mover_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": row.get("ticker", ""),
            "price": self._to_float(row.get("price")),
            "changeAmount": self._to_float(row.get("change_amount")),
            "changePercent": self._parse_percent(row.get("change_percentage")),
            "volume": self._to_float(row.get("volume")),
        }

    def _to_float(self, value: Any) -> float:
        if value in (None, "", "None"):
            return 0.0
        return float(value)

    def _parse_percent(self, value: Any) -> float:
        text = str(value or "").replace("%", "")
        return self._to_float(text)

    def _format_news_timestamp(self, value: str) -> str:
        if not value:
            return datetime.now(timezone.utc).isoformat()
        try:
            parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
            return parsed.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            return datetime.now(timezone.utc).isoformat()
