# verify-and-guard

name: verify-and-guard
description: run secret guard and verification gates before commit, push, PR, and merge.

## Trigger
- before commit
- before push
- before PR creation
- before merge or release actions

## Do Not Trigger
- when no files changed and no state transition is about to happen

## Rules
- run `scripts/no_secrets_guard.sh` first
- run `scripts/verify_minimal.sh` or a stricter targeted gate after the guard
- fail closed when secrets are detected
- record skipped checks with reasons
- do not print secret values, only file names or masked hints
