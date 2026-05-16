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
PYTHON_BIN = sys.executable


def python_command(*args: str) -> list[str]:
    return [PYTHON_BIN, *args]


STEP_GROUPS = {
    "text": [
        {"name": "text quality", "command": python_command("scripts/text_quality_guard.py")},
    ],
    "web": [
        {"name": "web lint", "command": [PNPM_BIN, "lint:web"]},
        {"name": "web typecheck", "command": [PNPM_BIN, "typecheck:web"]},
        {"name": "web build", "command": [PNPM_BIN, "build:web"]},
    ],
}
STEP_GROUPS["standard"] = [
    *STEP_GROUPS["text"],
    {"name": "no secrets guard", "command": python_command("scripts/no_secrets_guard.py")},
    *STEP_GROUPS["web"],
]
STEP_GROUPS["release"] = [
    {"name": "release readiness", "command": python_command("scripts/verify_release_readiness.py")}
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
