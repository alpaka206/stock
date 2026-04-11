        #!/usr/bin/env bash
        set -euo pipefail

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"

        MAX_ITERATIONS="${MAX_ITERATIONS:-30}"
        mkdir -p .omx/runtime .omx/journal

        for ((i=1; i<=MAX_ITERATIONS; i++)); do
          printf '%s
' "$(date -u +%Y-%m-%dT%H:%M:%SZ) iteration=$i" > .omx/runtime/heartbeat.txt
          printf '# Loop Iteration %s

- started_at: %s
- next: read .omx/state/NEXT_PROMPT.md and execute the top P0 item
' "$i" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > ".omx/journal/loop-$(printf '%02d' "$i").md"
          ./scripts/no_secrets_guard.sh || break
          ./scripts/verify_minimal.sh || true
          if grep -q '\[ \]' .omx/state/BACKLOG.md; then
            continue
          fi
          break
        done
