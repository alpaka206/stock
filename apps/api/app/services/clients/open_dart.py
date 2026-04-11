from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.services.errors import ExternalRateLimitError, ExternalServiceError


class OpenDartClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def get_recent_disclosures(
        self,
        *,
        days: int = 7,
        page_count: int = 20,
        corp_cls: str = "Y",
    ) -> list[dict[str, Any]]:
        if not self.api_key:
            raise ExternalServiceError("\uad6d\ub0b4 \uacf5\uc2dc\ub97c \ubcf4\ub824\uba74 OPENDART_API_KEY\uac00 \ud544\uc694\ud569\ub2c8\ub2e4.")

        end_date = datetime.now(timezone.utc).date()
        begin_date = end_date - timedelta(days=max(days, 1) - 1)
        payload = await self._request(
            {
                "crtfc_key": self.api_key,
                "bgn_de": begin_date.strftime("%Y%m%d"),
                "end_de": end_date.strftime("%Y%m%d"),
                "corp_cls": corp_cls,
                "sort": "date",
                "sort_mth": "desc",
                "page_no": "1",
                "page_count": str(page_count),
            }
        )
        rows = payload.get("list", [])
        if not rows:
            return []

        items: list[dict[str, Any]] = []
        for row in rows:
            receipt_no = str(row.get("rcept_no", "")).strip()
            items.append(
                {
                    "corpName": str(row.get("corp_name", "")).strip(),
                    "stockCode": str(row.get("stock_code", "")).strip(),
                    "reportName": str(row.get("report_nm", "")).strip(),
                    "receiptDate": str(row.get("rcept_dt", "")).strip(),
                    "filerName": str(row.get("flr_nm", "")).strip(),
                    "url": (
                        f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt_no}"
                        if receipt_no
                        else ""
                    ),
                }
            )
        return items

    async def _request(self, params: dict[str, str]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(f"{self.base_url}/list.json", params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ExternalRateLimitError("OpenDART \uc694\uccad\uc774 rate limit\uc5d0 \uac78\ub838\uc2b5\ub2c8\ub2e4.") from exc
            raise ExternalServiceError(
                f"OpenDART \uc694\uccad\uc774 HTTP {exc.response.status_code}\ub85c \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("OpenDART \uc694\uccad\uc774 \uc2dc\uac04 \ucd08\uacfc\ub418\uc5c8\uc2b5\ub2c8\ub2e4.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("OpenDART \uc694\uccad \uc911 \ub124\ud2b8\uc6cc\ud06c \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.") from exc
        except ValueError as exc:
            raise ExternalServiceError("OpenDART \uc751\ub2f5 JSON\uc744 \ud574\uc11d\ud558\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.") from exc

        status = str(payload.get("status", ""))
        if status not in {"000", "013"}:
            message = payload.get("message") or payload.get("status") or "unknown"
            raise ExternalServiceError(f"OpenDART \uc751\ub2f5 \uc624\ub958: {message}")
        return payload
