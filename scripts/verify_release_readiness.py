from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_RELEASE_ENV = (
    "STOCK_API_BASE_URL",
    "RESEARCH_ALLOW_FIXTURE_FALLBACK",
)

BACKEND_PROBE_PATHS = (
    "/actuator/health/readiness",
    "/v3/api-docs",
    "/overview",
    "/radar",
    "/stocks/NVDA",
    "/history",
    "/news",
    "/calendar",
    "/instruments/search?q=NVDA",
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify release readiness against the Spring backend."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_env_file(ROOT / "apps" / "web" / ".env")

    checks = check_env()
    hard_failures = [check for check in checks if not check["ok"]]
    route_results: list[dict[str, Any]] = []

    if not hard_failures:
        route_results = probe_backend(os.environ["STOCK_API_BASE_URL"].strip())
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


def check_env() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for env_name in REQUIRED_RELEASE_ENV:
        env_value = os.getenv(env_name, "").strip()
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

    fallback_value = os.getenv("RESEARCH_ALLOW_FIXTURE_FALLBACK", "").strip().lower()
    checks.append(
        {
            "name": "env::fixture-fallback",
            "ok": fallback_value == "false",
            "detail": (
                "릴리스 검증에서는 목데이터 fallback을 차단합니다."
                if fallback_value == "false"
                else "릴리스 검증은 RESEARCH_ALLOW_FIXTURE_FALLBACK=false 이어야 합니다."
            ),
        }
    )
    return checks


def probe_backend(base_url: str) -> list[dict[str, Any]]:
    return [probe_path(base_url, path) for path in BACKEND_PROBE_PATHS]


def probe_path(base_url: str, path: str) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "stock-release-readiness/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            content_type = response.headers.get("content-type", "")
            body = response.read(200).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        content_type = exc.headers.get("content-type", "")
        body = exc.read(200).decode("utf-8", errors="replace")
    except Exception as exc:
        return {
            "name": f"route::{path}",
            "ok": False,
            "detail": f"요청 실패: {exc}",
        }

    ok = 200 <= status < 300 and is_json_content_type(content_type)
    return {
        "name": f"route::{path}",
        "ok": ok,
        "detail": "2xx JSON 응답" if ok else f"HTTP {status} / {body}",
    }


def is_json_content_type(content_type: str) -> bool:
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


if __name__ == "__main__":
    raise SystemExit(main())
