from __future__ import annotations

import argparse
import os
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PNPM_BIN = "pnpm.cmd" if os.name == "nt" else "pnpm"
PY_COMPILE_TARGETS = [
    "apps/api/app/main.py",
    "apps/api/app/schemas/common.py",
    "apps/api/app/schemas/overview.py",
    "apps/api/app/schemas/radar.py",
    "apps/api/app/schemas/stocks.py",
    "apps/api/app/schemas/history.py",
    "apps/api/app/schemas/news.py",
    "apps/api/app/schemas/calendar.py",
    "apps/api/app/services/clients/alpha_vantage.py",
    "apps/api/app/services/clients/open_dart.py",
    "apps/api/app/services/clients/openai_responses.py",
    "apps/api/app/services/clients/gemini_responses.py",
    "apps/api/app/services/clients/summary_router.py",
    "apps/api/app/services/clients/yahoo_market.py",
    "apps/api/app/services/deterministic_summary.py",
    "apps/api/app/services/readiness.py",
    "apps/api/app/services/providers/mock.py",
    "apps/api/app/services/providers/real.py",
    "apps/api/app/services/providers/extended_mock.py",
    "apps/api/app/services/providers/extended_real.py",
]

STEP_GROUPS = {
    "text": [
        {"name": "text quality", "command": ["python", "scripts/text_quality_guard.py"]},
    ],
    "automation": [
        {"name": "omx contract parsing", "command": ["python", "scripts/test_omx_contract_parsing.py"]},
        {"name": "release PR manual merge policy", "command": ["python", "scripts/test_release_pr_policy.py"]},
        {"name": "no secrets guard", "command": ["python", "scripts/no_secrets_guard.py"]},
        {"name": "discord bridge smoke", "command": ["python", "scripts/test_discord_bridge.py"]},
        {"name": "discord latest-only helper", "command": ["python", "scripts/test_verify_discord_latest_only.py"]},
    ],
    "web": [
        {"name": "web lint", "command": [PNPM_BIN, "lint:web"]},
        {"name": "web typecheck", "command": [PNPM_BIN, "typecheck:web"]},
        {"name": "web build", "command": [PNPM_BIN, "build:web"]},
    ],
    "api": [
        {"name": "contract parity", "command": [PNPM_BIN, "check:contracts"]},
        {
            "name": "api py_compile",
            "command": ["python", "-m", "py_compile", *PY_COMPILE_TARGETS],
        },
        {"name": "api smoke", "command": ["python", "scripts/api_smoke.py"]},
    ],
}
STEP_GROUPS["standard"] = [*STEP_GROUPS["text"], *STEP_GROUPS["automation"], *STEP_GROUPS["web"], *STEP_GROUPS["api"]]
STEP_GROUPS["release"] = [
    {"name": "release readiness", "command": ["python", "scripts/verify_release_readiness.py"]}
]


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def tail_lines(text: str, limit: int = 20) -> list[str]:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    if len(lines) <= limit:
        return lines
    return lines[-limit:]


def run_step(name: str, command: list[str], *, json_mode: bool) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except FileNotFoundError as exc:
        exit_code = 127
        stdout = ""
        stderr = str(exc)

    duration_seconds = round(time.perf_counter() - started, 2)

    if not json_mode:
        print(f"==> {name}")
        print(f"$ {' '.join(command)}")
        if stdout.strip():
            print(stdout.rstrip())
        if stderr.strip():
            print(stderr.rstrip())
        print(f"[exit {exit_code}] {duration_seconds:.2f}s")
        print()

    return {
        "name": name,
        "command": command,
        "exit_code": exit_code,
        "duration_seconds": duration_seconds,
        "stdout_tail": tail_lines(stdout),
        "stderr_tail": tail_lines(stderr),
        "ok": exit_code == 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the stock workspace verification steps with a single deterministic entrypoint."
    )
    parser.add_argument(
        "--group",
        choices=sorted(STEP_GROUPS.keys()),
        default="standard",
        help="Verification scope to run. Default: standard",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary instead of streaming step logs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    steps = STEP_GROUPS[args.group]
    results = [run_step(step["name"], step["command"], json_mode=args.json) for step in steps]
    success = all(result["ok"] for result in results)
    summary = {
        "group": args.group,
        "root": str(ROOT),
        "success": success,
        "steps": results,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        status = "passed" if success else "failed"
        print(f"Verification {status}: {args.group}")
        for result in results:
            marker = "OK" if result["ok"] else "FAIL"
            print(f"- [{marker}] {result['name']} ({result['duration_seconds']:.2f}s)")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
