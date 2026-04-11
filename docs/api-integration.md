# API Integration

## Current Status
- Alpha Vantage backs global market data, news, rates, earnings, and IPO calendar paths.
- OpenDART backs domestic disclosure and event coverage.
- OpenAI and Gemini are optional summary providers for `/overview`, `/radar`, `/stocks/[symbol]`, and `/history`.
- `/news` and `/calendar` remain deterministic-first surfaces.

## Provider Strategy
- Alpha Vantage: market and news source
- OpenDART: domestic disclosure source
- OpenAI: optional structured summary source
- Gemini: free-tier summary alternative
- Deterministic fallback: last-resort summary path when no AI provider is available

## Fallback Order
1. OpenAI
2. Gemini
3. Deterministic summary

## Risks
- Free-tier quotas are low for sustained production traffic.
- Shared cache and retry/backoff remain limited.
- Domestic market coverage is still narrower than the target product scope.
- Optional LLM paths reduce hard failure risk, but they do not eliminate provider drift risk.

## Next Work
- Strengthen provider retry/backoff and request logging
- Add deeper unit coverage for provider parsing paths
- Expand domestic market/event coverage
