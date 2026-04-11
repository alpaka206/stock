# Stock Workspace

Stock Workspace is a research-oriented monorepo for viewing market context, watchlists, stock detail, history, news, and event calendars in one flow.

## Product Shape

Primary routes:
1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

Auxiliary routes:
- `/news`
- `/calendar`

`watchlist` stays inside `/radar` rather than becoming a top-level route.

## Repository Layout
- `apps/web`: Next.js frontend
- `apps/api`: FastAPI backend
- `packages/contracts`: shared schemas and TypeScript types
- `docs`: architecture, deployment, env, test, ADR, prompt notes
- `scripts`: verification and automation helpers
- `.omx`: repo-local autonomous runtime state, journals, bootstrap skills

## Local Development

Web:
```powershell
pnpm install
pnpm dev:web
```

API:
```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## Verification
```powershell
pnpm verify:standard
```

Focused slices:
```powershell
pnpm verify:web
pnpm verify:api
python scripts/api_smoke.py
```

## Runtime Notes
- Web expects a separate API target via `STOCK_API_BASE_URL` or route-specific env vars.
- API supports `OpenAI -> Gemini -> deterministic fallback` for summary generation.
- `.env.discord` is optional and local-only. It is never committed or printed.
