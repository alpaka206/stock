#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DISCORD_ENV_FILE="${DISCORD_ENV_FILE:-omx_discord_bridge/.env.discord}"
if [[ ! -f "$DISCORD_ENV_FILE" ]]; then
  echo "[discord-bridge] env file missing: $DISCORD_ENV_FILE"
  exit 1
fi

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[discord-bridge] python executable not found"
  exit 1
fi

mkdir -p .omx/runtime
export DISCORD_ENV_FILE
export PYTHONUTF8=1
echo "[discord-bridge] starting with env=$DISCORD_ENV_FILE"
"$PYTHON_BIN" omx_discord_bridge/discord_omx_bridge.py 2>&1 | tee .omx/runtime/discord-bridge-live.log
