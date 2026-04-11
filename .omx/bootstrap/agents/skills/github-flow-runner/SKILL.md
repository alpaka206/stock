# github-flow-runner

name: github-flow-runner
description: run issue-first branch flow, PR creation, and release automation in non-interactive mode.

## Trigger
- only when `ENABLE_GITHUB_AUTOMATION=true`
- only when `gh` is installed and authenticated
- when issue creation, branch creation, PR creation, or merge evaluation is required

## Do Not Trigger
- when `gh` is unavailable or unauthenticated
- when current work is on a permanent branch
- when the secret guard or review gate has not passed

## Rules
- read ISSUE_PR_POLICY, REVIEW_FEEDBACK_POLICY, and RELEASE_TO_MAIN_POLICY before acting
- do not delete, force-push, or directly push to `main` or `develop`
- require `scripts/no_secrets_guard.sh`, verification, and review gate pass before push or PR
- keep review feedback on the same branch and the same PR
- use squash merge for issue branch -> develop, merge commit for develop -> main
