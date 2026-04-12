from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.errors import ExternalServiceError


class YahooMarketClient:
    def __init__(self, *, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds
        self.base_headers = {"User-Agent": "Mozilla/5.0"}

    async def get_daily_series(self, symbol: str, limit: int = 100) -> list[dict[str, Any]]:
        payload = await self._request_json(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            params={
                "range": "1y",
                "interval": "1d",
                "includePrePost": "false",
                "events": "div,splits",
            },
        )
        chart = ((payload.get("chart") or {}).get("result") or [None])[0] or {}
        timestamps = chart.get("timestamp") or []
        quote = ((chart.get("indicators") or {}).get("quote") or [None])[0] or {}
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        volumes = quote.get("volume") or []

        rows: list[dict[str, Any]] = []
        for idx, raw_timestamp in enumerate(timestamps):
            close = closes[idx] if idx < len(closes) else None
            if close in (None, ""):
                continue
            opened = opens[idx] if idx < len(opens) else close
            high = highs[idx] if idx < len(highs) else close
            low = lows[idx] if idx < len(lows) else close
            volume = volumes[idx] if idx < len(volumes) and volumes[idx] is not None else 0.0
            rows.append(
                {
                    "date": datetime.fromtimestamp(int(raw_timestamp), tz=timezone.utc).date().isoformat(),
                    "open": float(opened or close),
                    "high": float(high or close),
                    "low": float(low or close),
                    "close": float(close),
                    "volume": float(volume),
                }
            )

        if len(rows) < 2:
            raise ExternalServiceError(f"{symbol} Yahoo chart series is unavailable.")

        rows.reverse()
        return rows[:limit]

    async def get_company_overview(self, symbol: str) -> dict[str, Any]:
        payload = await self._request_json(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={"q": symbol},
        )
        quotes = payload.get("quotes") or []
        normalized_symbol = symbol.upper()
        quote = next(
            (
                item
                for item in quotes
                if str(item.get("symbol", "")).upper() == normalized_symbol
                and str(item.get("quoteType", "")).upper() == "EQUITY"
            ),
            None,
        )
        if not quote:
            raise ExternalServiceError(f"{symbol} Yahoo search overview is unavailable.")

        sector = self._map_sector(
            str(quote.get("industryDisp") or quote.get("industry") or quote.get("sectorDisp") or quote.get("sector") or "")
        )
        return {
            "symbol": normalized_symbol,
            "name": quote.get("longname") or quote.get("shortname") or normalized_symbol,
            "sector": sector,
            "industry": quote.get("industryDisp") or quote.get("industry") or "",
            "description": "",
            "marketCapitalization": 0.0,
            "peratio": 0.0,
            "analystTargetPrice": 0.0,
            "exchange": quote.get("exchDisp") or quote.get("exchange") or "",
        }

    async def _request_json(self, url: str, *, params: dict[str, str]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, headers=self.base_headers) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(f"Yahoo request failed with HTTP {exc.response.status_code}.") from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Yahoo request timed out.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("Yahoo request failed with a network error.") from exc
        except ValueError as exc:
            raise ExternalServiceError("Yahoo response returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise ExternalServiceError("Yahoo response type was invalid.")
        return payload

    def _map_sector(self, value: str) -> str:
        normalized = value.strip().lower()
        if "semiconductor" in normalized:
            return "반도체"
        if "software" in normalized:
            return "소프트웨어"
        if "security" in normalized:
            return "사이버보안"
        if "power" in normalized or "utility" in normalized:
            return "전력 인프라"
        if "technology" in normalized:
            return "기술주"
        return value.strip() or "미분류"
