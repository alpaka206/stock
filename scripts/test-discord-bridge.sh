#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DISCORD_ENV_FILE="${DISCORD_ENV_FILE:-omx_discord_bridge/.env.discord}"
DISCORD_BRIDGE_PORT="${DISCORD_BRIDGE_PORT:-8787}"

if [[ ! -f "$DISCORD_ENV_FILE" ]]; then
  echo "[discord-bridge-test] env file missing: $DISCORD_ENV_FILE"
  exit 1
fi

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[discord-bridge-test] python executable not found"
  exit 1
fi

export DISCORD_ENV_FILE
export DISCORD_BRIDGE_PORT
"$PYTHON_BIN" omx_discord_bridge/discord_omx_bridge.py > .omx/runtime/discord-bridge.log 2>&1 &
BRIDGE_PID=$!
trap 'kill $BRIDGE_PID 2>/dev/null || true' EXIT

sleep 2
curl -s "http://127.0.0.1:${DISCORD_BRIDGE_PORT}/health"
echo

"$PYTHON_BIN" - <<'PY'
import json
import os
from urllib import request

port = int(os.getenv('DISCORD_BRIDGE_PORT', '8787'))
roles = ['planner', 'critic', 'researcher', 'architect', 'executor', 'verifier']
for role in roles:
    payload = json.dumps(
        {
            'username': role,
            'content': f'[{role}] bridge smoke message',
            'meeting_id': 'bridge-smoke',
            'phase': role,
            'trigger_id': 'bridge-smoke',
        }
    ).encode('utf-8')
    req = request.Request(
        f'http://127.0.0.1:{port}/event',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with request.urlopen(req, timeout=15) as response:
        print(response.read().decode('utf-8'))
PY

curl -s -X POST "http://127.0.0.1:${DISCORD_BRIDGE_PORT}/sync-replies"
echo
