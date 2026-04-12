#!/usr/bin/env bash
set -euo pipefail

DISCORD_BRIDGE_PORT="${DISCORD_BRIDGE_PORT:-8787}"
curl -s -X POST "http://127.0.0.1:${DISCORD_BRIDGE_PORT}/sync-replies"
echo
