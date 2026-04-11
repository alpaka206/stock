#!/usr/bin/env bash
        set -euo pipefail

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"

        DISCORD_ENV_FILE="${DISCORD_ENV_FILE:-.env.discord}"
        REQUIRED_KEYS=(DISCORD_GUILD_ID DISCORD_PARENT_CHANNEL_ID DISCORD_WEBHOOK_URL ALLOWED_DISCORD_USER_IDS DISCORD_BOT_TOKEN)

        if [[ ! -f "$DISCORD_ENV_FILE" ]]; then
          echo "[discord-bridge] missing env file: $DISCORD_ENV_FILE"
          exit 1
        fi

        missing=0
        for key in "${REQUIRED_KEYS[@]}"; do
          if grep -q "^${key}=" "$DISCORD_ENV_FILE"; then
            echo "[discord-bridge] key present: $key"
          else
            echo "[discord-bridge] key missing: $key"
            missing=1
          fi
        done

        python - <<'PY'
import importlib.util
mods = ['httpx']
for mod in mods:
    print(f"[discord-bridge] python module {'ok' if importlib.util.find_spec(mod) else 'missing'}: {mod}")
PY

        exit "$missing"
