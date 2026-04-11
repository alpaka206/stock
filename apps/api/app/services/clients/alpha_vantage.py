from __future__ import annotations

from csv import DictReader
from datetime import datetime, timezone
from hashlib import sha1
from io import StringIO
from typing import Any
import json
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
        self._cache: dict[str, tuple[float, Any]] = {}

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
        latest_value = self._to_float(latest.get("value"))
        previous_value = latest_value
        if len(series) > 1:
            previous_value = self._to_float(series[1].get("value"))

        change_percent = 0.0
        if previous_value:
            change_percent = ((latest_value - previous_value) / previous_value) * 100

        return {
            "date": latest.get("date", ""),
            "value": latest_value,
            "changePercent": round(change_percent, 2),
        }

    async def get_earnings_calendar(
        self, *, symbol: str | None = None, horizon: str = "3month"
    ) -> list[dict[str, Any]]:
        params = {"function": "EARNINGS_CALENDAR", "horizon": horizon}
        if symbol:
            params["symbol"] = symbol
        rows = await self._request_csv(params)
        items: list[dict[str, Any]] = []
        for row in rows:
            ticker = row.get("symbol", "").strip().upper()
            if not ticker:
                continue
            items.append(
                {
                    "symbol": ticker,
                    "name": row.get("name", "").strip() or ticker,
                    "reportDate": row.get("reportDate", "").strip(),
                    "fiscalDateEnding": row.get("fiscalDateEnding", "").strip(),
                    "estimate": self._to_float(row.get("estimate")),
                    "currency": row.get("currency", "").strip(),
                }
            )
        return items

    async def get_ipo_calendar(self) -> list[dict[str, Any]]:
        rows = await self._request_csv({"function": "IPO_CALENDAR"})
        items: list[dict[str, Any]] = []
        for row in rows:
            symbol = row.get("symbol", "").strip().upper()
            if not symbol:
                continue
            items.append(
                {
                    "symbol": symbol,
                    "name": row.get("name", "").strip() or symbol,
                    "ipoDate": row.get("ipoDate", "").strip(),
                    "priceRangeLow": self._to_float(row.get("priceRangeLow")),
                    "priceRangeHigh": self._to_float(row.get("priceRangeHigh")),
                    "currency": row.get("currency", "").strip(),
                    "exchange": row.get("exchange", "").strip(),
                }
            )
        return items

    async def _request(self, params: dict[str, str]) -> dict[str, Any]:
        payload = await self._request_raw(params, datatype="json")
        if not isinstance(payload, dict):
            raise ExternalServiceError("Alpha Vantage JSON response type was invalid.")
        return payload

    async def _request_csv(self, params: dict[str, str]) -> list[dict[str, str]]:
        payload = await self._request_raw(params, datatype="csv")
        if not isinstance(payload, str):
            raise ExternalServiceError("Alpha Vantage CSV response type was invalid.")
        self._raise_for_csv_errors(payload, self._describe_request(params))
        reader = DictReader(StringIO(payload))
        return [
            {key: (value or "").strip() for key, value in row.items() if key}
            for row in reader
        ]

    async def _request_raw(self, params: dict[str, str], *, datatype: str) -> Any:
        if not self.api_key:
            raise ProviderConfigurationError(
                "ALPHA_VANTAGE_API_KEY is required for real provider mode."
            )

        merged = {**params, "apikey": self.api_key}
        if datatype == "csv":
            merged["datatype"] = "csv"
        cache_key = self._cache_key(merged)
        now = time.time()
        if cache_key in self._cache:
            expires_at, cached_payload = self._cache[cache_key]
            if expires_at > now:
                return cached_payload

        request_target = self._describe_request(params)
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.base_url, params=merged)
                response.raise_for_status()
                if datatype == "csv":
                    payload = response.text
                else:
                    payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 429:
                raise ExternalRateLimitError(
                    f"Alpha Vantage {request_target} hit a rate limit."
                ) from exc
            raise ExternalServiceError(
                f"Alpha Vantage {request_target} failed with HTTP {status_code}."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                f"Alpha Vantage {request_target} timed out."
            ) from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError(
                f"Alpha Vantage {request_target} failed with a network error."
            ) from exc
        except ValueError as exc:
            raise ExternalServiceError(
                f"Alpha Vantage {request_target} returned invalid {datatype.upper()} data."
            ) from exc

        if datatype == "json":
            self._raise_for_provider_errors(payload)
        self._cache[cache_key] = (now + self.cache_ttl_seconds, payload)
        return payload

    def _raise_for_provider_errors(self, payload: dict[str, Any]) -> None:
        note = payload.get("Note") or payload.get("Information")
        if note:
            raise ExternalRateLimitError(str(note))

        if "Error Message" in payload:
            raise ExternalServiceError(str(payload["Error Message"]))

    def _raise_for_csv_errors(self, payload: str, request_target: str) -> None:
        normalized = payload.strip()
        if not normalized:
            raise ExternalServiceError(f"Alpha Vantage {request_target} returned an empty CSV payload.")
        if normalized.startswith("{"):
            parsed = json.loads(normalized)
            self._raise_for_provider_errors(parsed)
            raise ExternalServiceError(f"Alpha Vantage {request_target} returned an empty CSV payload.")

    def _cache_key(self, params: dict[str, str]) -> str:
        serialized = "&".join(f"{key}={params[key]}" for key in sorted(params))
        return sha1(serialized.encode("utf-8")).hexdigest()

    def _describe_request(self, params: dict[str, str]) -> str:
        parts = [params.get("function", "unknown")]
        if symbol := params.get("symbol"):
            parts.append(symbol)
        elif tickers := params.get("tickers"):
            parts.append(tickers)
        return " ".join(parts)

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
