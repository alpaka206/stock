# 테스트 전략

## 표준 게이트

```bash
pnpm verify:standard
```

포함 항목:

- 텍스트 품질 검사
- 비밀 값 가드
- 웹 lint/typecheck/build

## 릴리스 게이트

Spring 백엔드가 실행 중인 상태에서 아래를 실행한다.

```bash
pnpm verify:release
```

확인 항목:

- `STOCK_API_BASE_URL`
- `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`
- Spring `/actuator/health/readiness`
- Spring `/v3/api-docs`
- 핵심 화면 API `/overview`, `/radar`, `/stocks/NVDA`, `/history`
- 보조 API `/news`, `/calendar`, `/instruments/search?q=NVDA`

## 브라우저 게이트

```bash
pnpm test:e2e
```

확인 경로:

- `/overview`
- `/radar`
- `/stocks/NVDA`
- `/history?symbol=NVDA`
- 레이더 검색에서 종목 상세 이동
- 종목 차트, 지표, 패턴 카드
- 스냅샷 저장 후 히스토리 조회

## 백엔드 게이트

```bash
cd ../stock_BE
.\mvnw.cmd test
```

Swagger는 `/v3/api-docs`와 `/swagger-ui.html`로 확인한다.

## 보안 게이트

```bash
pnpm audit --audit-level low
pnpm --dir apps/web audit --audit-level low
```

GitHub에서는 `dependency-review`, `codeql (javascript-typescript)`을 PR 필수 체크로 둔다.

## 데이터 확인

- 실제 API 응답이면 출처와 기준 시각을 확인한다.
- fallback이면 화면에 `(목데이터)`가 표시되어야 한다.
- 서버 관리 값은 Next 서버 라우트와 Spring 백엔드 저장 API를 함께 확인한다.
