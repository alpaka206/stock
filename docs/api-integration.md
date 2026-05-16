# API 연동 문서

## 현재 구조

- Web: Next.js App Router
- Backend: 별도 저장소 `../stock_BE`의 Spring Boot API
- 계약: `packages/contracts`
- 운영 저장소: Spring Boot 백엔드의 Postgres + Flyway migration
- 인증: 백엔드 `HttpOnly` access/refresh cookie

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
- `GET /csrf`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /v3/api-docs`
- `GET /swagger-ui.html`

## 프런트 연결

- 기본 백엔드 URL은 `STOCK_API_BASE_URL=http://localhost:8080`이다.
- route별 URL이 필요한 경우 `OVERVIEW_API_URL`, `RADAR_API_URL`, `STOCK_DETAIL_API_URL`, `HISTORY_API_URL`, `NEWS_API_URL`, `CALENDAR_API_URL`, `INSTRUMENT_SEARCH_API_URL`, `SNAPSHOT_API_URL`로 덮어쓴다.
- `POST /snapshots`, `DELETE /snapshots/{id}` 같은 mutation은 Next 서버 라우트가 백엔드 `/csrf`를 먼저 조회한 뒤 CSRF header와 cookie를 함께 전달한다.
- 프런트 JavaScript는 access token, refresh token 원문을 저장하지 않는다.

## 데이터 제공자

- Alpha Vantage: 미국장 가격, 시계열, 뉴스, 경제 지표
- OpenDART: 국내 공시
- SEC EDGAR: 미국 공시
- Perso: 어닝콜, 연준 발표 등 오디오/영상 더빙 및 자막 작업
- LLM provider: 추후 리포트 요약과 이메일 발송 자동화에 연결

## fallback 규칙

1. 실제 백엔드 응답 사용
2. 백엔드가 mock sourceRef를 반환하면 화면에 `(목데이터)` 표시
3. API가 없거나 실패하면 개발 환경에서만 fixture fallback 허용
4. 운영 후보에서는 `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`

## 백엔드 저장 원칙

- 시장 데이터, 뉴스, 공시, 사용자 판단 기록, 리포트 예약, 미디어 작업 상태는 백엔드 저장소에서 관리한다.
- 프런트는 `STOCK_API_BASE_URL`과 `packages/contracts` 계약만 의존한다.
- 저장 API는 백엔드에서 트랜잭션, 외래키, cascade 정책을 관리한다.
