#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REVIEW_FILE="${1:-.omx/state/CODE_REVIEW_STATUS.md}"

if [[ ! -f "$REVIEW_FILE" ]]; then
  echo "[review-gate] missing review file: $REVIEW_FILE"
  exit 1
fi

if grep -qi '^status:[[:space:]]*APPROVE' "$REVIEW_FILE"; then
  echo '[review-gate] approved'
  exit 0
fi

if grep -qi '^blocking_findings:[[:space:]]*0' "$REVIEW_FILE"; then
  echo '[review-gate] no blocking findings'
  exit 0
fi

echo '[review-gate] blocked'
exit 1
