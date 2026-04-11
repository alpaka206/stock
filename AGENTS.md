# Autonomous Repo Contract

Repository purpose: stock research workspace.

Primary routes:
1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

Read first:
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/codex/prompt-order.md`

## Top-level contract
- PRIMARY_TASK: build a site that surfaces the information and analysis needed for stock research
- MIN_EXIT_CONDITION: charts, real-time global news, and disclosures are usable; QA is complete; main is updated; `https://stock-mu-seven.vercel.app/overview` works
- AUTO_CONTINUE_POLICY: keep choosing the next smallest verifiable task until MIN_EXIT_CONDITION is met
- RELEASE_TO_MAIN_POLICY: auto-merge-if-green
- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `.env.discord`

## Core rules
- Do not ask the user for confirmation when a safe default exists.
- Keep iterations small and verifiable.
- Verification and secret safety come before convenience.
- Never fabricate prices, news, levels, or scores without sources.
- `.env`, `.env.*`, `.env.discord`, `.env.discord.*`, key/cert/token files and values must never be printed, committed, or pushed.
- `.env.discord` is read-only secret input. Only file existence and key presence may be checked.

## Multi-agent consensus
- For large or risky work, run a short internal loop: planner -> critic -> architect -> executor.
- Record the conclusion in `.omx/journal/` or `.omx/state/*`.
- Do not loop on planning without moving to the next executable step.

## Infinite operation
- `scripts/omx-loop.sh` supports infinite operation with `MAX_ITERATIONS=0` or `INFINITE_MODE=true`.
- Heartbeat, watchdog, and journal output must stay current.
- After 3 consecutive failures, stop repeating the same tactic and record the cause and next fallback.

## Git flow
- Permanent branches: `main`, `develop`
- No direct push, force push, hard reset, or deletion on permanent branches.
- Use issue-linked branches from `develop`.
- Review feedback stays on the same branch and PR.
- RELEASE_TO_MAIN_POLICY is the single control point for main automation.

## Review gate
1. Implement
2. lint / build / test
3. Codex review
4. no blocking issue or explicit approve
5. then push / PR / develop integration
