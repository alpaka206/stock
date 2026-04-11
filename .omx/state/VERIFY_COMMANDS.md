# Verify Commands

Detected commands:
- `pnpm verify:standard`
- `pnpm verify:web`
- `pnpm verify:api`
- `pnpm check:contracts`
- `python scripts/api_smoke.py`

Default policy:
1. use `pnpm verify:standard` when possible
2. rerun narrower web/api checks for failure isolation
3. run `scripts/no_secrets_guard.sh` before commit, push, PR, and merge
