#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for name in TASK STATE BACKLOG NEXT_PROMPT DISCORD_STATUS VERIFY_LAST_FAILURE; do
  path=".omx/state/${name}.md"
  [[ -f "$path" ]] || continue
  echo "== ${name} =="
  cat "$path"
  echo
done
