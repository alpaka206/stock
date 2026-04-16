from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    command = [sys.executable, "scripts/verify_workspace.py", "--group", "standard"]
    print(f"[verify] {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
