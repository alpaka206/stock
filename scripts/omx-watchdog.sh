        #!/usr/bin/env bash
        set -euo pipefail

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"

        mkdir -p .omx/runtime
        HEARTBEAT_FILE=.omx/runtime/heartbeat.txt
        STALL_SECONDS="${STALL_SECONDS:-900}"
        now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

        if [[ -f "$HEARTBEAT_FILE" ]]; then
          last_epoch="$(stat -c %Y "$HEARTBEAT_FILE" 2>/dev/null || stat -f %m "$HEARTBEAT_FILE")"
          current_epoch="$(date +%s)"
          age=$(( current_epoch - last_epoch ))
          if (( age > STALL_SECONDS )); then
            printf '# Watchdog

- stalled_at: %s
- age_seconds: %s
- action: investigate current iteration and refresh state files
' "$now" "$age" > .omx/runtime/watchdog-status.md
          fi
        fi

        printf '%s
' "$now" > "$HEARTBEAT_FILE"
