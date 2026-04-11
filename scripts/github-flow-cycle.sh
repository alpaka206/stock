        #!/usr/bin/env bash
        set -euo pipefail

        # ??? main ???? ???
        RELEASE_TO_MAIN_POLICY="auto-merge-if-green"
        INTEGRATION_BRANCH="develop"
        PRODUCTION_BRANCH="main"
        GH_BIN="${GH_BIN:-C:/Program Files/GitHub CLI/gh.exe}"

        export GH_PROMPT_DISABLED=1
        export GIT_TERMINAL_PROMPT=0
        export CI=1

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"
        mkdir -p .omx/runtime

        if [[ ! -x "$GH_BIN" ]] && ! command -v gh >/dev/null 2>&1; then
          printf 'github-flow deferred: gh not installed
' > .omx/runtime/github-flow-status.txt
          exit 0
        fi

        GH_CMD="$GH_BIN"
        if [[ ! -x "$GH_CMD" ]]; then
          GH_CMD="gh"
        fi

        current_branch="$(git branch --show-current)"
        if [[ "$current_branch" == "$INTEGRATION_BRANCH" || "$current_branch" == "$PRODUCTION_BRANCH" ]]; then
          printf 'github-flow blocked: current branch is permanent (%s)
' "$current_branch" > .omx/runtime/github-flow-status.txt
          exit 1
        fi

        ./scripts/no_secrets_guard.sh
        ./scripts/verify_minimal.sh
        ./scripts/codex-review-gate.sh

        if ! "$GH_CMD" auth status >/dev/null 2>&1; then
          printf 'github-flow deferred: gh installed but not authenticated
' > .omx/runtime/github-flow-status.txt
          exit 0
        fi

        printf 'github-flow ready: local gates passed (lint/build/test + Codex review)
' > .omx/runtime/github-flow-status.txt
        exit 0
