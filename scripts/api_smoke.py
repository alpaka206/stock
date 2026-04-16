from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel, ValidationError


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402
from app.schemas.calendar import CalendarResponse  # noqa: E402
from app.schemas.history import HistoryResponse  # noqa: E402
from app.schemas.news import NewsResponse  # noqa: E402
from app.schemas.overview import OverviewResponse  # noqa: E402
from app.schemas.radar import RadarResponse  # noqa: E402
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
)


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

    if failures:
        print("API smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("API smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
