# Test Strategy

## Standard Gate
- web lint
- web typecheck
- web build
- contract parity
- api py_compile
- api smoke

## Notes
- `scripts/api_smoke.py` launches a temporary uvicorn process and verifies routes over real HTTP.
- `pnpm verify:standard` is the unattended close-out gate.
- Discord bridge health is separate from the main app gate.

## Additional Checks
- `scripts/no_secrets_guard.sh`
- `scripts/codex-review-gate.sh`
- `scripts/check-discord-bridge.sh` (expected to fail cleanly when `.env.discord` is absent)
