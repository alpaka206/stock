# 환경변수 체크리스트

## Web

- `STOCK_API_BASE_URL`: Spring 백엔드 기본 URL. 로컬 기본값은 `http://localhost:8080`
- `OVERVIEW_API_URL`
- `RADAR_API_URL`
- `STOCK_DETAIL_API_URL`
- `HISTORY_API_URL`
- `NEWS_API_URL`
- `CALENDAR_API_URL`
- `SNAPSHOT_API_URL`
- `INSTRUMENT_SEARCH_API_URL`
- `OVERVIEW_API_TIMEOUT_MS`
- `RESEARCH_ALLOW_FIXTURE_FALLBACK`
- `NEXT_PUBLIC_SITE_URL`

## Backend

백엔드 환경변수는 `../stock_BE/.env.example`을 기준으로 둔다.

- `DATABASE_URL`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`
- `REDIS_HOST`, `REDIS_PORT`
- `CORS_ALLOWED_ORIGINS`
- `AUTH_JWT_SECRET`
- `AUTH_COOKIE_SECURE`
- `AUTH_COOKIE_DOMAIN`
- `AUTH_FRONTEND_CALLBACK_URL`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `ALPHA_VANTAGE_API_KEY`
- `OPENDART_API_KEY`
- `SEC_USER_AGENT`
- `PERSO_API_KEY`

## 로컬 권장값

```env
STOCK_API_BASE_URL=http://localhost:8080
RESEARCH_ALLOW_FIXTURE_FALLBACK=true
```

## 운영 후보 권장값

```env
RESEARCH_ALLOW_FIXTURE_FALLBACK=false
NEXT_PUBLIC_SITE_URL=https://실제-도메인
```

백엔드는 운영에서 `AUTH_COOKIE_SECURE=true`, 32자 이상의 `AUTH_JWT_SECRET`, 실제 provider API 키를 설정한다.

## 보안

- `.env`, `.env.*`는 커밋하지 않는다.
- API 키와 토큰 값은 로그, PR, 문서에 쓰지 않는다.
- 문서에는 placeholder만 적고 실제 값은 배포 환경변수 저장소에서 관리한다.
