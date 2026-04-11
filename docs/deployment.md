# Deployment

## Current Status
- The repository assumes split deployment.
- Web and API are separate runtimes.
- `/health` is liveness only.
- `/readyz` is the readiness endpoint.

## Recommended Topology
- Web: Vercel
- API: Render / Railway / equivalent Python hosting
- Optional DB later: Turso for user data and cache

## Release Gate
1. `pnpm verify:standard`
2. Real API env configured
3. Web API target configured
4. `/health` and `/readyz` pass
5. Smoke target routes

## Required Runtime Targets
- Frontend must know the public API base URL
- Backend must have the required provider env vars
- `RESEARCH_ALLOW_FIXTURE_FALLBACK=false` is recommended for deployment-like environments

## Remaining Risks
- Free hosting spin-down can slow cold starts
- Alpha Vantage quota remains a production risk
- Branch protection rulesets are not yet configured remotely
