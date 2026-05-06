from __future__ import annotations

from typing import Any

import httpx

from app.services.errors import ExternalRateLimitError, ExternalServiceError

MATERIAL_FORMS = {"10-K", "10-Q", "8-K", "6-K", "S-1", "DEF 14A"}


class SecFilingsClient:
    def __init__(
        self,
        *,
        base_url: str,
        user_agent: str,
        timeout_seconds: float,
        cik_by_symbol: dict[str, str],
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.cik_by_symbol = {
            symbol.upper(): cik.zfill(10)
            for symbol, cik in cik_by_symbol.items()
            if symbol.strip() and cik.strip()
        }

    async def get_recent_filings(
        self,
        *,
        symbols: list[str],
        limit_per_symbol: int = 2,
    ) -> list[dict[str, Any]]:
        filings: list[dict[str, Any]] = []
        for symbol in symbols:
            normalized_symbol = symbol.upper()
            cik = self.cik_by_symbol.get(normalized_symbol)
            if not cik:
                continue

            try:
                filings.extend(
                    await self._get_symbol_filings(
                        symbol=normalized_symbol,
                        cik=cik,
                        limit=limit_per_symbol,
                    )
                )
            except ExternalServiceError:
                continue

        return sorted(
            filings,
            key=lambda item: str(item.get("filingDate", "")),
            reverse=True,
        )

    async def _get_symbol_filings(
        self,
        *,
        symbol: str,
        cik: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        payload = await self._request(f"/submissions/CIK{cik}.json")
        company_name = str(payload.get("name", symbol)).strip() or symbol
        recent = payload.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        documents = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])

        filings: list[dict[str, Any]] = []
        for index, form in enumerate(forms):
            form_name = str(form).strip()
            if form_name not in MATERIAL_FORMS:
                continue

            accession_number = self._list_value(accession_numbers, index)
            primary_document = self._list_value(documents, index)
            filings.append(
                {
                    "symbol": symbol,
                    "companyName": company_name,
                    "cik": cik,
                    "form": form_name,
                    "filingDate": self._list_value(filing_dates, index),
                    "reportDate": self._list_value(report_dates, index),
                    "description": self._list_value(descriptions, index) or form_name,
                    "accessionNumber": accession_number,
                    "url": self._filing_url(
                        cik=cik,
                        accession_number=accession_number,
                        primary_document=primary_document,
                    ),
                }
            )
            if len(filings) >= limit:
                break

        return filings

    async def _request(self, path: str) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    f"{self.base_url}{path}",
                    headers={
                        "Accept": "application/json",
                        "User-Agent": self.user_agent,
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ExternalRateLimitError("SEC filings request hit a rate limit.") from exc
            raise ExternalServiceError(
                f"SEC filings request failed with HTTP {exc.response.status_code}."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("SEC filings request timed out.") from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError("SEC filings network request failed.") from exc
        except ValueError as exc:
            raise ExternalServiceError("SEC filings JSON response could not be parsed.") from exc

    def _filing_url(
        self,
        *,
        cik: str,
        accession_number: str,
        primary_document: str,
    ) -> str:
        if not accession_number or not primary_document:
            return ""

        compact_accession = accession_number.replace("-", "")
        return (
            "https://www.sec.gov/Archives/edgar/data/"
            f"{int(cik)}/{compact_accession}/{primary_document}"
        )

    def _list_value(self, values: Any, index: int) -> str:
        if not isinstance(values, list) or index >= len(values):
            return ""
        return str(values[index] or "").strip()
