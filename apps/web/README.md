# apps/web

Next.js frontend for the stock research workspace.

## Routes
Primary routes:
- `/overview`
- `/radar`
- `/stocks/[symbol]`
- `/history`

Auxiliary routes:
- `/news`
- `/calendar`

`watchlist` remains part of `/radar`.

## Local Run
```powershell
pnpm install
pnpm dev:web
```

## Verification
```powershell
pnpm verify:web
```

## Runtime Environment
- `STOCK_API_BASE_URL`
- `OVERVIEW_API_URL`
- `RADAR_API_URL`
- `STOCK_DETAIL_API_URL`
- `HISTORY_API_URL`
- `NEWS_API_URL`
- `CALENDAR_API_URL`
- `OVERVIEW_API_TIMEOUT_MS`
- `RESEARCH_ALLOW_FIXTURE_FALLBACK`

## Notes
- Route files stay thin.
- Feature logic stays under `features/*`.
- API-first loading is preferred.
- Fixture fallback must be explicit, not silent.
