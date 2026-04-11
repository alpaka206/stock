#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo '== TASK =='
cat .omx/state/TASK.md
echo
echo '== STATE =='
cat .omx/state/STATE.md
echo
echo '== BACKLOG =='
cat .omx/state/BACKLOG.md
echo
echo '== GIT WORKFLOW =='
cat .omx/state/GIT_WORKFLOW_STATUS.md
