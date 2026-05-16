# Stock Desk

미국 주식과 한국 주식을 한 흐름으로 읽는 주식 리서치 워크스페이스입니다. 시장 개요, 관심 종목 레이더, 종목별 차트와 분석, 뉴스, 공시, 이벤트 히스토리, 판단 기록을 한곳에서 확인하는 것을 목표로 합니다.

## 주요 화면

1. `/overview` - 시장 흐름, 지수, 섹터, 뉴스, 위험 요인
2. `/radar` - 관심 종목 검색, 정렬, 섹터/태그 필터, 감지 알림
3. `/stocks/[symbol]` - 가격 차트, 기술적 신호, 뉴스와 공시, 판단 기록
4. `/history` - 과거 이벤트와 가격 반응 복기

보조 화면은 `/news`, `/calendar`를 유지합니다.

## 저장소 구조

- `apps/web`: Next.js 프런트엔드
- `apps/api`: FastAPI 백엔드
- `packages/contracts`: 프런트와 백엔드가 공유하는 타입/스키마 계약
- `docs`: 아키텍처, API 연동, 배포, 운영 문서
- `scripts`: 검증과 스모크 테스트

## 로컬 실행

```powershell
pnpm install
pnpm dev:web
```

```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

프런트에서 API를 붙일 때는 `apps/web/.env`에 아래처럼 설정합니다.

```env
STOCK_API_BASE_URL=http://localhost:8000
RESEARCH_ALLOW_FIXTURE_FALLBACK=true
```

## Docker 실행

Docker Compose는 `web`, `api`, `db(Postgres)`를 함께 실행합니다.

```powershell
docker compose up --build
```

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- DB: `localhost:5432`

운영에서는 `POSTGRES_PASSWORD`, 실제 API 키, `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`를 환경변수로 주입합니다. `.env` 파일은 커밋하지 않습니다.

## 데이터 원칙

- 실제 API가 있으면 서버에서 받아 캐시하고 프런트는 서버 응답을 사용합니다.
- API가 없거나 실패해 fixture/fallback을 보여주면 화면에 `(목데이터)`를 표시합니다.
- 판단 기록은 서버 API에 저장합니다.
- `DATABASE_URL`이 있으면 API는 Postgres 트랜잭션으로 저장하고, 없으면 개발용 파일 저장소를 사용합니다.

## 검증

```powershell
pnpm verify:standard
pnpm verify:release
```

부분 검증:

```powershell
pnpm verify:web
pnpm verify:api
python scripts/api_smoke.py
```

## GitHub 흐름

- 보호 브랜치: `develop`, `main`
- 작업 브랜치: `feat/<issue>-<slug>` 또는 `fix/<issue>-<slug>`
- PR 흐름: issue branch -> `develop`, 이후 릴리스 시 `develop -> main`
- `main`, `develop` 직접 push와 force push 금지
- 커밋/PR 제목은 `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `ci:`, `test:`, `perf:` 형식을 사용합니다.

## English Summary

Stock Desk is a research workspace for US and Korean equities. It connects market overview, watchlist radar, stock detail analysis, event history, filings, news, and saved research notes. The web app is built with Next.js, the API with FastAPI, and shared contracts live in `packages/contracts`.
