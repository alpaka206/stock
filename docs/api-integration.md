# API 연동 문서

## 현재 구조

- Web: Next.js App Router
- API: FastAPI
- 계약: `packages/contracts`
- 운영 저장소: `DATABASE_URL`이 있으면 Postgres 사용
- 개발 fallback: `RESEARCH_SNAPSHOT_STORE_PATH` 또는 `data/runtime/research_snapshots.json`

## 주요 API

- `GET /overview`
- `GET /radar`
- `GET /stocks/{symbol}`
- `GET /history`
- `GET /news`
- `GET /calendar`
- `GET /instruments/search?q=...`
- `GET /snapshots`
- `POST /snapshots`
- `DELETE /snapshots/{id}`

## 데이터 제공자

- Alpha Vantage: 미국장 가격, 시계열, 뉴스, 경제 지표
- OpenDART: 국내 공시
- OpenAI 또는 Gemini: 선택 요약 provider
- deterministic summary: LLM 키가 없을 때의 마지막 요약 경로

## fallback 규칙

1. 실제 API 응답 사용
2. API가 mock sourceRef만 반환하면 화면에 `(목데이터)` 표시
3. API가 없거나 실패하면 개발 환경에서만 fixture fallback 허용
4. 운영 후보에서는 `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`

## 백엔드 분리 기준

`stock_BE` 저장소는 현재 빈 저장소다. API 규모가 커지면 아래 기준으로 분리한다.

- DB migration과 배치 작업이 프런트 배포 주기와 달라질 때
- 시세/뉴스/공시 캐시와 사용자 데이터가 별도 권한 모델을 요구할 때
- n8n 또는 워커 기반 수집 파이프라인이 독립 배포되어야 할 때

분리 후에도 프런트는 `STOCK_API_BASE_URL`과 `packages/contracts` 계약만 의존해야 한다.
