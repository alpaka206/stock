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
messages = [
    (
        'coordinator',
        'Discord 회의형 브리지 스모크 테스트를 시작합니다. 역할들이 서로 이어서 말하는 형식이 보이는지 확인해 주세요.',
    ),
    (
        'planner',
        '이번 요청의 핵심은 Discord에서 실제로 읽히는 회의 흐름입니다. 한 줄 상태 보고보다 역할 간 응답 구조를 먼저 만들 필요가 있다고 봅니다.',
    ),
    (
        'critic',
        'planner 의견에는 동의하지만, 읽기 쉬운 한국어와 과한 로그 노출 방지도 같이 잡아야 합니다. 그렇지 않으면 실제 사용 단계에서 금방 피로해집니다.',
    ),
    (
        'researcher',
        '현재 브리지는 송수신은 되지만 메시지가 스모크 로그처럼 보입니다. 테스트도 대화형 샘플로 바꾸면 사용감 검증이 쉬워집니다.',
    ),
    (
        'architect',
        '그러면 역할별 JSON에 team_message와 reply_to를 넣고, Discord에는 그 필드만 읽기 좋게 풀어서 보내는 구조가 맞겠습니다.',
    ),
    (
        'executor',
        '우선 회의형 포맷과 테스트 스크립트를 정리하고, 실제 사용자는 채널에 한 줄 남기면 루프가 한국어로 이어받아 답하는 흐름으로 검증하겠습니다.',
    ),
    (
        'verifier',
        '현재 단계에서는 회의형 메시지 가독성과 실제 송수신 여부를 먼저 확인하면 충분합니다. 사용자가 채널에 메시지를 보내면 import 로그까지 같이 보겠습니다.',
    ),
]
for role, content in messages:
    payload = json.dumps(
        {
            'username': role,
            'content': content,
            'meeting_id': 'bridge-dialogue-smoke',
            'phase': role,
            'trigger_id': 'bridge-dialogue-smoke',
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
