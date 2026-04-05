#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DISCORD_ENV_FILE="${DISCORD_ENV_FILE:-omx_discord_bridge/.env.discord}"
if [[ ! -f "$DISCORD_ENV_FILE" ]]; then
  echo "[discord-bridge] env file missing: $DISCORD_ENV_FILE"
  exit 1
fi

export DISCORD_ENV_FILE
python omx_discord_bridge/discord_omx_bridge.py
