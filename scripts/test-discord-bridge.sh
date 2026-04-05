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

export DISCORD_ENV_FILE
export DISCORD_BRIDGE_PORT
python omx_discord_bridge/discord_omx_bridge.py > .omx/runtime/discord-bridge.log 2>&1 &
BRIDGE_PID=$!
trap 'kill $BRIDGE_PID 2>/dev/null || true' EXIT

sleep 2
curl -s "http://127.0.0.1:${DISCORD_BRIDGE_PORT}/health"
echo

python - <<'PY'
import os
import time
import httpx

port = int(os.getenv('DISCORD_BRIDGE_PORT', '8787'))
roles = ['planner', 'critic', 'architect', 'executor']
for role in roles:
    payload = {
        'username': role,
        'content': f'[{role}] 1회 테스트 메시지',
    }
    response = httpx.post(f'http://127.0.0.1:{port}/event', json=payload, timeout=15.0)
    print(response.text)
    time.sleep(1)
PY

curl -s -X POST "http://127.0.0.1:${DISCORD_BRIDGE_PORT}/sync-replies"
echo
