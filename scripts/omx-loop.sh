#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MAX_ITERATIONS="${MAX_ITERATIONS:-30}"
INFINITE_MODE="${INFINITE_MODE:-false}"
mkdir -p .omx/runtime .omx/journal .omx/state

iteration=1
while true; do
  printf '%s
' "$(date -u +%Y-%m-%dT%H:%M:%SZ) iteration=$iteration" > .omx/runtime/heartbeat.txt
  printf '# Loop Iteration %s

- started_at: %s
- consensus: planner -> critic -> architect -> executor
- next: read .omx/state/NEXT_PROMPT.md and execute the top P0 item
' "$iteration" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > ".omx/journal/loop-$(printf '%04d' "$iteration").md"
  ./scripts/no_secrets_guard.sh || break

  if ./scripts/verify_minimal.sh > .omx/runtime/verify-last.log 2>&1; then
    cat > .omx/state/VERIFY_LAST_FAILURE.md <<'EOF'
# Verify Last Failure

status: clear
failing_command:
symptom:
likely_cause:
remediation_owner:
next_fix:
EOF
  else
    cat > .omx/state/VERIFY_LAST_FAILURE.md <<'EOF'
# Verify Last Failure

status: active
failing_command: scripts/verify_minimal.sh
symptom: verification command returned non-zero
likely_cause: inspect .omx/runtime/verify-last.log
remediation_owner: current iteration
next_fix: fix the failing verification item and rerun the same command first
EOF
  fi

  if [[ "$INFINITE_MODE" != "true" && "$MAX_ITERATIONS" != "0" && "$iteration" -ge "$MAX_ITERATIONS" ]]; then
    break
  fi

  iteration=$((iteration + 1))
done
