from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel, ValidationError


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
SNAPSHOT_SMOKE_STORE = ROOT / "data" / "runtime" / "api_smoke_snapshots.json"
os.environ["RESEARCH_SNAPSHOT_STORE_PATH"] = str(SNAPSHOT_SMOKE_STORE)
SNAPSHOT_SMOKE_STORE.unlink(missing_ok=True)
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.main import app  # noqa: E402
from app.schemas.calendar import CalendarResponse  # noqa: E402
from app.schemas.history import HistoryResponse  # noqa: E402
from app.schemas.news import NewsResponse  # noqa: E402
from app.schemas.overview import OverviewResponse  # noqa: E402
from app.schemas.radar import RadarResponse  # noqa: E402
from app.schemas.search import InstrumentSearchResponse  # noqa: E402
from app.schemas.snapshots import (  # noqa: E402
    SnapshotDeleteResponse,
    SnapshotListResponse,
    SnapshotMutationResponse,
)
from app.schemas.stocks import StockDetailResponse  # noqa: E402


@dataclass(frozen=True)
class RouteCheck:
    path: str
    model: type[BaseModel]


ROUTES = (
    RouteCheck("/overview", OverviewResponse),
    RouteCheck("/radar", RadarResponse),
    RouteCheck("/stocks/NVDA", StockDetailResponse),
    RouteCheck("/history", HistoryResponse),
    RouteCheck("/news", NewsResponse),
    RouteCheck("/calendar", CalendarResponse),
    RouteCheck("/instruments/search?q=nvda", InstrumentSearchResponse),
    RouteCheck("/snapshots", SnapshotListResponse),
)

SNAPSHOT_PAYLOAD = {
    "id": "api-smoke-snapshot",
    "createdAt": "2026-05-06T00:00:00+00:00",
    "symbol": "NVDA",
    "name": "NVIDIA",
    "exchange": "NASDAQ",
    "securityCode": "NVDA-US",
    "sector": "Semiconductors",
    "note": "API smoke snapshot",
    "stance": "bullish",
    "conviction": "medium",
    "price": 923.42,
    "changePercent": 2.16,
    "score": 82,
    "thesis": "Smoke test payload",
    "selectedEventTitle": "Earnings",
    "selectedEventDate": "2026-03-13",
    "activeRuleLabels": ["MA trend"],
    "presetName": "Default",
}


async def main() -> int:
    failures: list[str] = []
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        timeout=15.0,
    ) as client:
        readiness_response = await client.get("/readyz", params={"probe": "config"})
        print(f"GET /readyz?probe=config -> {readiness_response.status_code}")
        if readiness_response.status_code != 200:
            failures.append(
                f"/readyz?probe=config: expected 200, got {readiness_response.status_code}"
            )
        elif "application/json" not in readiness_response.headers.get("content-type", ""):
            failures.append("/readyz?probe=config: expected application/json response")
        else:
            readiness_payload = readiness_response.json()
            if readiness_payload.get("status") != "ready":
                failures.append("/readyz?probe=config: expected status=ready")

        for route in ROUTES:
            response = await client.get(route.path)
            print(f"GET {route.path} -> {response.status_code}")
            if response.status_code != 200:
                failures.append(f"{route.path}: expected 200, got {response.status_code}")
                continue

            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                failures.append(
                    f"{route.path}: expected application/json, got {content_type or 'missing'}"
                )
                continue

            try:
                route.model.model_validate(response.json())
            except ValidationError as exc:
                failures.append(
                    f"{route.path}: schema validation failed -> {exc.errors()[:1]}"
                )

        create_response = await client.post("/snapshots", json=SNAPSHOT_PAYLOAD)
        print(f"POST /snapshots -> {create_response.status_code}")
        if create_response.status_code != 200:
            failures.append(
                f"/snapshots POST: expected 200, got {create_response.status_code}"
            )
        else:
            try:
                SnapshotMutationResponse.model_validate(create_response.json())
            except ValidationError as exc:
                failures.append(
                    f"/snapshots POST: schema validation failed -> {exc.errors()[:1]}"
                )

        symbol_response = await client.get("/snapshots", params={"symbol": "NVDA"})
        print(f"GET /snapshots?symbol=NVDA -> {symbol_response.status_code}")
        if symbol_response.status_code != 200:
            failures.append(
                f"/snapshots?symbol=NVDA: expected 200, got {symbol_response.status_code}"
            )
        else:
            try:
                payload = SnapshotListResponse.model_validate(symbol_response.json())
                if not any(
                    snapshot.id == SNAPSHOT_PAYLOAD["id"]
                    for snapshot in payload.snapshots
                ):
                    failures.append("/snapshots?symbol=NVDA: created snapshot missing")
            except ValidationError as exc:
                failures.append(
                    f"/snapshots?symbol=NVDA: schema validation failed -> {exc.errors()[:1]}"
                )

        delete_response = await client.delete(f"/snapshots/{SNAPSHOT_PAYLOAD['id']}")
        print(f"DELETE /snapshots/{SNAPSHOT_PAYLOAD['id']} -> {delete_response.status_code}")
        if delete_response.status_code != 200:
            failures.append(
                f"/snapshots DELETE: expected 200, got {delete_response.status_code}"
            )
        else:
            try:
                payload = SnapshotDeleteResponse.model_validate(delete_response.json())
                if not payload.deleted:
                    failures.append("/snapshots DELETE: expected deleted=true")
            except ValidationError as exc:
                failures.append(
                    f"/snapshots DELETE: schema validation failed -> {exc.errors()[:1]}"
                )

    if failures:
        print("API smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("API smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
