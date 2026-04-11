# Verify Commands

Detected commands:
- `python scripts/text_quality_guard.py`
- `pnpm verify:standard`
- `pnpm verify:web`
- `pnpm verify:api`
- `pnpm check:contracts`
- `python scripts/api_smoke.py`

Default policy:
1. run `python scripts/text_quality_guard.py`
2. run `pnpm verify:standard`
3. if verification fails, write the failure into `VERIFY_LAST_FAILURE.md`
4. treat failure remediation as the next highest-priority task
5. rerun the failed command first, then rerun the broader gate
6. run `scripts/no_secrets_guard.sh` before commit, push, PR, and merge
