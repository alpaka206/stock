# verification-remediator

name: verification-remediator
description: turn any failed guard, lint, build, test, or smoke result into the top remediation task and keep rerunning until the failure is resolved or explicitly blocked.

## Trigger
- when `scripts/no_secrets_guard.sh` fails
- when `scripts/verify_minimal.sh` or `pnpm verify:standard` fails
- when any release, smoke, or quality gate returns non-zero

## Do Not Trigger
- when all gates are already green
- when the only blocker is a missing external secret or permission that has already been recorded

## Rules
- failed verification becomes the next highest-priority task
- record the failing command, failing symptom, likely cause, and next fix in state or journal
- do not continue unrelated feature work until the failure is fixed or explicitly classified as blocked
- rerun the same failed command first, then rerun the broader gate
- do not hide failures with silent fallback or by skipping the gate
