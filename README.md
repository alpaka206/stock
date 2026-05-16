# Stock Desk

미국 주식과 한국 주식을 한 흐름으로 읽는 주식 리서치 워크스페이스입니다. 시장 개요, 관심 종목 레이더, 종목별 차트와 분석, 뉴스, 공시, 이벤트 히스토리, 판단 기록을 한곳에서 확인하는 것을 목표로 합니다.

## 주요 화면

1. `/overview` - 시장 흐름, 지수, 섹터, 뉴스, 위험 요인
2. `/radar` - 관심 종목 검색, 정렬, 섹터/태그 필터, 감지 알림
3. `/stocks/[symbol]` - 가격 차트, 기술적 신호, 뉴스와 공시, 판단 기록
4. `/history` - 과거 이벤트와 가격 반응 복기

보조 화면은 `/news`, `/calendar`, `/workspace`를 유지합니다.

- `/workspace` - 로그인, 구독 플랜, 리포트 이메일, Perso 더빙/자막 작업 관리

## 저장소 구조

- `apps/web`: Next.js 프런트엔드와 서버 라우트
- `packages/contracts`: 프런트와 백엔드가 공유하는 타입/스키마 계약
- `docs`: 아키텍처, API 연동, 배포, 운영 문서
- `scripts`: 프런트 검증과 릴리스 점검
- 백엔드: 별도 저장소 `../stock_BE` 또는 `https://github.com/alpaka206/stock_BE`

## 로컬 실행

Spring Boot 백엔드를 먼저 실행합니다.

```powershell
cd ..\stock_BE
.\mvnw.cmd spring-boot:run
```

프런트는 이 저장소에서 실행합니다.

```powershell
pnpm install
pnpm dev:web
```

`apps/web/.env`는 아래 값을 기준으로 둡니다.

```env
STOCK_API_BASE_URL=http://localhost:8080
RESEARCH_ALLOW_FIXTURE_FALLBACK=true
```

## Docker 실행

이 저장소의 Docker Compose는 프런트만 실행하고, API는 외부 Spring Boot 백엔드에 연결합니다.

```powershell
docker compose up --build
```

- Web: `http://localhost:3000`
- API: 기본값 `http://host.docker.internal:8080`
- Swagger: `http://localhost:8080/swagger-ui.html`

## 데이터 원칙

- 실제 API가 있으면 백엔드에서 받아 저장하고, 프런트는 백엔드 응답을 사용합니다.
- API가 없거나 실패해 fixture/fallback을 보여주면 화면에 `(목데이터)`를 표시합니다.
- 판단 기록, 저장된 보기, 리포트 예약, 미디어 작업 상태처럼 서버에서 관리해야 하는 값은 백엔드 저장소를 기준으로 합니다.
- 인증 토큰은 프런트 JavaScript가 직접 저장하지 않고, 백엔드가 `HttpOnly` cookie로 관리합니다.
- `/workspace`의 구독 플랜은 기능 제한을 보여주지만, 실제 접근 제한은 결제/구독 정책이 확정된 뒤 백엔드에서 적용합니다.

## 검증

```powershell
pnpm verify:standard
```

릴리스 전에는 Spring 백엔드를 켠 상태에서 아래를 실행합니다.

```powershell
pnpm verify:release
```

백엔드 검증은 `../stock_BE`에서 실행합니다.

```powershell
.\mvnw.cmd test
```

## GitHub 흐름

- 보호 브랜치: `develop`, `main`
- 작업 브랜치: `feat/<issue>-<slug>` 또는 `fix/<issue>-<slug>`
- PR 흐름: issue branch -> `develop`, 이후 릴리스 시 `develop -> main`
- `main`, `develop` 직접 push와 force push 금지
- squash merge 금지
- 커밋/PR 제목은 `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `ci:`, `test:`, `perf:` 형식을 사용합니다.

## English Summary

Stock Desk is a research workspace for US and Korean equities. The frontend is built with Next.js, the production backend lives in the Spring Boot repository `stock_BE`, and shared contracts live in `packages/contracts`.
