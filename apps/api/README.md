# Stock Workspace API

FastAPI backend for the stock research workspace.

## Routes
Main routes:
- `/overview`
- `/radar`
- `/stocks/{symbol}`
- `/history`

Auxiliary routes:
- `/news`
- `/calendar`

Operational routes:
- `/health`
- `/readyz`
- `/docs`
- `/redoc`

## Local Run
```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## Summary Provider Modes
- `RESEARCH_LLM_PROVIDER=auto`: OpenAI first, Gemini second, deterministic fallback last
- `RESEARCH_LLM_PROVIDER=openai`: OpenAI only
- `RESEARCH_LLM_PROVIDER=gemini`: Gemini only
- `RESEARCH_LLM_PROVIDER=none`: deterministic summary only

## Data Sources
- Alpha Vantage: prices, news, rates, earnings calendar, IPO calendar
- OpenDART: domestic disclosures
- OpenAI / Gemini: optional structured summaries for the main four pages

## Verification
```powershell
python ../../scripts/api_smoke.py
python ../../scripts/verify_workspace.py --group api
```

## Deployment Notes
- Split deployment is assumed: frontend and API are separate services.
- `/health` is liveness only.
- `/readyz?probe=config|remote` is the readiness path.
