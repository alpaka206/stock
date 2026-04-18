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

## Codex Quick Start
- Open [stock.code-workspace](C:\Users\김규원\Desktop\stock\stock.code-workspace) in VS Code or Cursor.
- Codex repo-local plugin metadata lives under `.agents/plugins/marketplace.json` and `plugins/stock-omx-loop/`.
- Start the bridge on Windows with `powershell -ExecutionPolicy Bypass -File scripts/run-discord-bridge.ps1`.
- Start the autonomous loop on Windows with `powershell -ExecutionPolicy Bypass -File scripts/omx-loop.ps1 -InfiniteMode`.
- Set `OMX_DISCORD_MODE=signal-only` in `omx_discord_bridge/.env.discord` if you want Discord to receive only user-facing signals instead of every role message.

## Ralph Loop
- Project-level Ralph settings live in `.ralph-loop.yml`.
- Runtime collision controls live in `.ralph-loop.yml > runtime`.
- Repo-local Codex config lives in `.codex/`.
- Local branch safety hooks live in `.githooks/`.
- Runtime resolver lives in `scripts/ralph_runtime.py`.
- Bootstrap another repo with `powershell -ExecutionPolicy Bypass -File scripts/ralph-init.ps1 -TargetRepo C:\path\to\repo`.
- Start the Codex-native Ralph runner with `powershell -ExecutionPolicy Bypass -File scripts/ralph-run.ps1`.
- Validate the Ralph setup with `pnpm verify:ralph`.
- Validate runtime resolution with `python scripts/test_ralph_runtime.py`.
- Discord control commands:
  - `/ralph status`
  - `/ralph pause`
  - `/ralph resume`
  - `/ralph stop`
  - `/ralph nudge <message>`
  - `/ralph goal <message>`
  - `/ralph done <message>`
  - `/ralph logs`
  - `/ralph pr`

## Reuse Layout
- `.ralph-loop.yml`: project goal, done conditions, Discord routing, branch rules, runtime port and drive
- `.codex/`: Codex hooks, rules, agents
- `.githooks/`: local git safety guard
- `scripts/omx_autonomous_loop.py`: main loop engine
- `scripts/ralph_runtime.py`: per-repo runtime resolver
- `scripts/ralph-init.ps1`: one-time bootstrap installer for another repository
- `omx_discord_bridge/`: Discord bridge and polling logic
- `plugins/stock-omx-loop/`: repo-local skill and plugin bundle
