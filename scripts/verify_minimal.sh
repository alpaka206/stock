#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[verify] python executable not found"
  exit 1
fi

exec "$PYTHON_BIN" scripts/verify_minimal.py "$@"
