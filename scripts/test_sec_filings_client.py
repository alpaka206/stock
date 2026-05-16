from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.clients.sec_filings import SecFilingsClient  # noqa: E402

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class FakeSecFilingsClient(SecFilingsClient):
    async def _request(self, path: str) -> dict[str, Any]:
        assert path == "/submissions/CIK0001045810.json"
        return {
            "name": "NVIDIA CORP",
            "filings": {
                "recent": {
                    "form": ["4", "10-Q", "8-K", "10-K"],
                    "accessionNumber": [
                        "0000000000-26-000001",
                        "0001045810-26-000010",
                        "0001045810-26-000011",
                        "0001045810-26-000012",
                    ],
                    "filingDate": ["2026-05-04", "2026-05-03", "2026-05-02", "2026-05-01"],
                    "reportDate": ["2026-05-04", "2026-04-30", "2026-05-02", "2026-01-31"],
                    "primaryDocument": ["xslF345X05/doc.xml", "nvda-20260430.htm", "nvda-8k.htm", "nvda-10k.htm"],
                    "primaryDocDescription": ["FORM 4", "Quarterly report", "Current report", "Annual report"],
                }
            },
        }


async def main() -> int:
    client = FakeSecFilingsClient(
        base_url="https://data.sec.gov",
        user_agent="stock-workspace-test contact=test@example.com",
        timeout_seconds=1,
        cik_by_symbol={"NVDA": "1045810"},
    )
    filings = await client.get_recent_filings(symbols=["NVDA", "UNKNOWN"], limit_per_symbol=2)

    assert [filing["form"] for filing in filings] == ["10-Q", "8-K"]
    assert filings[0]["symbol"] == "NVDA"
    assert filings[0]["companyName"] == "NVIDIA CORP"
    assert "000104581026000010" in filings[0]["url"]
    assert filings[0]["url"].endswith("/nvda-20260430.htm")
    print("sec filings client tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
