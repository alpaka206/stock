#!/usr/bin/env bash
        set -euo pipefail

        ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        cd "$ROOT_DIR"

        exclude_regex='^(\.venv/|node_modules/|apps/web/\.next/|\.pnpm-store/|\.omx/logs/|\.omx/runtime/|dist/|coverage/)'
        banned_file_patterns=(
          '.env'
          '.env.*'
          '.env.discord'
          '.env.discord.*'
          '*.pem'
          '*.key'
          '*.p12'
          '*.pfx'
          '*.crt'
          '*.cer'
          '*.der'
          '*.jks'
          '*.kdb'
          '*.secrets.*'
        )

        high_risk_regex='BEGIN (RSA|EC|OPENSSH|PRIVATE KEY)|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,}|hooks\.slack\.com/services/[A-Za-z0-9/_-]+|discord\.com/api/webhooks/[A-Za-z0-9/_-]+|x-goog-api-key[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_-]{12,}'
        failed=0

        mapfile -t tracked_files < <(git ls-files | grep -Ev "$exclude_regex" || true)
        mapfile -t staged_files < <(git diff --cached --name-only | grep -Ev "$exclude_regex" || true)
        mapfile -t all_git_files < <(printf '%s
' "${tracked_files[@]}" "${staged_files[@]}" | awk 'NF' | sort -u)

        echo '[guard] checking tracked and staged file names'
        for pattern in "${banned_file_patterns[@]}"; do
          for file in "${all_git_files[@]}"; do
            [[ -z "$file" ]] && continue
            if [[ "$file" == $pattern ]]; then
              echo "[guard] banned filename match: $file"
              failed=1
            fi
          done
        done

        if git ls-files '.env.discord' '.env.discord.*' | grep -q .; then
          echo '[guard] tracked discord env file detected'
          failed=1
        fi
        if git diff --cached --name-only -- '.env.discord' '.env.discord.*' | grep -q .; then
          echo '[guard] staged discord env file detected'
          failed=1
        fi

        echo '[guard] scanning tracked and staged repo files for risky markers'
        for file in "${all_git_files[@]}"; do
          [[ -f "$file" ]] || continue
          if grep -nE "$high_risk_regex" "$file" >/tmp/no_secrets_guard_match.txt 2>/dev/null; then
            first_line="$(head -n 1 /tmp/no_secrets_guard_match.txt || true)"
            line_hint="${first_line%%:*}"
            echo "[guard] risky content hint: ${file}:${line_hint:-?}"
            failed=1
          fi
        done
        rm -f /tmp/no_secrets_guard_match.txt 2>/dev/null || true

        if [[ "$failed" -ne 0 ]]; then
          echo '[guard] failed'
          exit 1
        fi

        echo '[guard] passed'
