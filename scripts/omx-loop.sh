#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MAX_ITERATIONS="${MAX_ITERATIONS:-30}"
INFINITE_MODE="${INFINITE_MODE:-false}"
OMX_LOOP_INTERVAL_SECONDS="${OMX_LOOP_INTERVAL_SECONDS:-30}"
OMX_LOOP_ERROR_BACKOFF_SECONDS="${OMX_LOOP_ERROR_BACKOFF_SECONDS:-90}"
mkdir -p .omx/runtime .omx/journal .omx/state
export PYTHONUTF8=1

echo "[omx-loop] root=$ROOT_DIR infinite=$INFINITE_MODE interval=${OMX_LOOP_INTERVAL_SECONDS}s"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[omx-loop] python executable not found"
  exit 1
fi

iteration=1
while true; do
  printf '%s iteration=%s
' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$iteration" > .omx/runtime/heartbeat.txt
  export OMX_LOOP_ITERATION="$iteration"
  echo "[omx-loop] iteration=$iteration start"

  if "$PYTHON_BIN" scripts/omx_autonomous_loop.py 2>&1 | tee .omx/runtime/omx-loop-last.log; then
    echo "[omx-loop] iteration=$iteration ok"
  else
    printf '%s iteration=%s exit=1
' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$iteration" > .omx/runtime/omx-loop-error.txt
    echo "[omx-loop] iteration=$iteration failed; see .omx/runtime/omx-loop-last.log"
    sleep "$OMX_LOOP_ERROR_BACKOFF_SECONDS"
  fi

  if [[ "$INFINITE_MODE" != "true" && "$MAX_ITERATIONS" != "0" && "$iteration" -ge "$MAX_ITERATIONS" ]]; then
    break
  fi

  iteration=$((iteration + 1))
  sleep "$OMX_LOOP_INTERVAL_SECONDS"
done
