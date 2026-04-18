# Environment Checklist

## API
- `STOCK_API_PROVIDER`
- `STOCK_API_TIMEOUT_SECONDS`
- `STOCK_API_CACHE_TTL_SECONDS`
- `ALPHA_VANTAGE_API_KEY`
- `ALPHA_VANTAGE_BASE_URL`
- `OPENDART_API_KEY`
- `OPENDART_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `RESEARCH_LLM_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_BASE_URL`
- `STOCK_RADAR_SYMBOLS`
- `STOCK_RADAR_SECTORS`
- `STOCK_OVERVIEW_BENCHMARKS`
- `STOCK_SECTOR_PROXIES`

## Web
- `STOCK_API_BASE_URL`
- `OVERVIEW_API_URL`
- `RADAR_API_URL`
- `STOCK_DETAIL_API_URL`
- `HISTORY_API_URL`
- `NEWS_API_URL`
- `CALENDAR_API_URL`
- `OVERVIEW_API_TIMEOUT_MS`
- `RESEARCH_ALLOW_FIXTURE_FALLBACK`

## Discord
- `.env.discord` stays local-only
- Only key presence is checked
- Values are never printed or committed

## Recommended Local Mode
- API: `STOCK_API_PROVIDER=real`
- LLM: `RESEARCH_LLM_PROVIDER=auto` or `none`
- Web: `STOCK_API_BASE_URL=http://localhost:8000`

## Release-like Timeout Note
- `RESEARCH_ALLOW_FIXTURE_FALLBACK=false` 이고 원격 API URL을 직접 붙이는 경우에는 cold start를 고려해 웹 fetch 타임아웃을 최소 30초로 본다.
- `OVERVIEW_API_TIMEOUT_MS` 를 별도로 둘 때도 30000ms 이상을 권장한다.
