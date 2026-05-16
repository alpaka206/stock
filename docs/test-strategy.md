# 테스트 전략

## 표준 게이트

```bash
pnpm verify:standard
```

포함 항목:

- 텍스트 품질 검사
- 비밀 값 가드
- 웹 lint/typecheck/build
- 계약 parity 검사
- API 단위 smoke
- SEC filings, Alpha Vantage cache key, provider builder 검사

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

## 보안 게이트

```bash
pnpm audit --audit-level low
pnpm --dir apps/web audit --audit-level low
```

GitHub에서는 `dependency-review`, `codeql (javascript-typescript)`, `codeql (python)`을 PR 필수 체크로 둔다.

## 데이터 확인

- 실제 API 응답이면 출처와 기준 시각을 확인한다.
- fallback이면 화면에 `(목데이터)`가 표시되어야 한다.
- 서버 관리 값은 `/api/research-snapshots`와 API `/snapshots` 경로를 함께 확인한다.
