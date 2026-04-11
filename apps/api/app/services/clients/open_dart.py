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
            raise ExternalServiceError("국내 공시를 보려면 OPENDART_API_KEY가 필요합니다.")

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
                raise ExternalRateLimitError("OpenDART 요청이 rate limit에 걸렸습니다.") from exc
            raise ExternalServiceError(
                f"OpenDART 요청이 HTTP {exc.response.status_code}로 실패했습니다."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("OpenDART 요청이 시간 초과되었습니다.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("OpenDART 요청 중 네트워크 오류가 발생했습니다.") from exc
        except ValueError as exc:
            raise ExternalServiceError("OpenDART 응답 JSON을 해석하지 못했습니다.") from exc

        status = str(payload.get("status", ""))
        if status not in {"000", "013"}:
            message = payload.get("message") or payload.get("status") or "unknown"
            raise ExternalServiceError(f"OpenDART 응답 오류: {message}")
        return payload
