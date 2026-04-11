        #!/usr/bin/env bash
        set -euo pipefail

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"

        log() { printf '[verify] %s
' "$*"; }
        run_step() {
          local label="$1"
          shift
          log "$label"
          "$@"
        }

        if command -v pnpm >/dev/null 2>&1 && grep -q '"verify:standard"' package.json 2>/dev/null; then
          run_step 'pnpm verify:standard' pnpm verify:standard
          exit 0
        fi

        if command -v pnpm >/dev/null 2>&1 && grep -q '"lint:web"' package.json 2>/dev/null; then
          run_step 'pnpm lint:web' pnpm lint:web
        else
          log 'skip lint: no detected command'
        fi

        if command -v pnpm >/dev/null 2>&1 && grep -q '"typecheck:web"' package.json 2>/dev/null; then
          run_step 'pnpm typecheck:web' pnpm typecheck:web
        else
          log 'skip typecheck: no detected command'
        fi

        if command -v pnpm >/dev/null 2>&1 && grep -q '"build:web"' package.json 2>/dev/null; then
          run_step 'pnpm build:web' pnpm build:web
        else
          log 'skip build: no detected command'
        fi

        if [[ -f scripts/api_smoke.py ]]; then
          run_step 'python scripts/api_smoke.py' python scripts/api_smoke.py
        else
          log 'skip api smoke: script missing'
        fi
