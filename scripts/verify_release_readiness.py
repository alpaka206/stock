from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


REQUIRED_REAL_PROVIDER_ENV = (
    "ALPHA_VANTAGE_API_KEY",
    "OPENDART_API_KEY",
    "OPENAI_API_KEY",
)
REQUIRED_WEB_API_ENV = (
    "STOCK_API_BASE_URL",
    "OVERVIEW_API_URL",
    "RADAR_API_URL",
    "STOCK_DETAIL_API_URL",
    "HISTORY_API_URL",
    "NEWS_API_URL",
    "CALENDAR_API_URL",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify deploy-ready release gate for the stock workspace."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks: list[dict[str, Any]] = []

    checks.extend(check_api_env())
    checks.extend(check_web_env())

    hard_failures = [check for check in checks if not check["ok"]]
    route_results: list[dict[str, Any]] = []

    if not hard_failures:
        route_results = run_release_probe()
        hard_failures.extend(result for result in route_results if not result["ok"])

    success = not hard_failures
    summary = {
        "success": success,
        "checks": checks,
        "route_results": route_results,
        "blockers": [item["detail"] for item in hard_failures],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("== Release readiness ==")
        for check in checks:
            marker = "OK" if check["ok"] else "FAIL"
            print(f"- [{marker}] {check['name']}: {check['detail']}")
        for result in route_results:
            marker = "OK" if result["ok"] else "FAIL"
            print(f"- [{marker}] {result['name']}: {result['detail']}")
        print("Release readiness passed." if success else "Release readiness failed.")

    return 0 if success else 1


def check_api_env() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    provider_mode = os.getenv("STOCK_API_PROVIDER", "").strip().lower()
    checks.append(
        {
            "name": "env::STOCK_API_PROVIDER",
            "ok": provider_mode == "real",
            "detail": (
                "STOCK_API_PROVIDER=real 입니다."
                if provider_mode == "real"
                else "릴리스 검증은 STOCK_API_PROVIDER=real 이어야 합니다."
            ),
        }
    )
    for env_name in REQUIRED_REAL_PROVIDER_ENV:
        env_value = os.getenv(env_name)
        checks.append(
            {
                "name": f"env::{env_name}",
                "ok": bool(env_value),
                "detail": (
                    f"{env_name}가 설정되어 있습니다."
                    if env_value
                    else f"{env_name}가 비어 있습니다."
                ),
            }
        )
    return checks


def check_web_env() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    fallback_value = os.getenv("RESEARCH_ALLOW_FIXTURE_FALLBACK", "").strip().lower()
    checks.append(
        {
            "name": "env::RESEARCH_ALLOW_FIXTURE_FALLBACK",
            "ok": fallback_value == "false",
            "detail": (
                "RESEARCH_ALLOW_FIXTURE_FALLBACK=false 입니다."
                if fallback_value == "false"
                else "릴리스 검증은 RESEARCH_ALLOW_FIXTURE_FALLBACK=false 이어야 합니다."
            ),
        }
    )

    has_api_target = any(os.getenv(env_name) for env_name in REQUIRED_WEB_API_ENV)
    checks.append(
        {
            "name": "env::web-api-target",
            "ok": has_api_target,
            "detail": (
                "웹이 연결할 API URL 환경변수가 있습니다."
                if has_api_target
                else "STOCK_API_BASE_URL 또는 route별 API URL이 필요합니다."
            ),
        }
    )
    return checks


def run_release_probe() -> list[dict[str, Any]]:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    results: list[dict[str, Any]] = []

    readiness = client.get("/readyz?probe=remote")
    readiness_payload = readiness.json()
    results.append(
        {
            "name": "route::/readyz?probe=remote",
            "ok": readiness.status_code == 200 and readiness_payload.get("status") == "ready",
            "detail": (
                "실 provider 3종 readiness가 통과했습니다."
                if readiness.status_code == 200 and readiness_payload.get("status") == "ready"
                else f"실 provider readiness 실패: HTTP {readiness.status_code} / {readiness_payload}"
            ),
        }
    )

    for path in (
        "/overview",
        "/radar",
        "/stocks/NVDA",
        "/history",
        "/news",
        "/calendar",
    ):
        response = client.get(path)
        results.append(
            {
                "name": f"route::{path}",
                "ok": response.status_code == 200
                and "application/json" in response.headers.get("content-type", ""),
                "detail": (
                    "200 JSON 응답"
                    if response.status_code == 200
                    and "application/json" in response.headers.get("content-type", "")
                    else f"HTTP {response.status_code} / {response.text[:200]}"
                ),
            }
        )

    return results


if __name__ == "__main__":
    raise SystemExit(main())
