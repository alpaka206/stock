# 테스트 전략

## 표준 게이트

- `pnpm guard:no-secrets`
- `pnpm lint:web`
- `pnpm typecheck:web`
- `pnpm build:web`
- `python scripts/check_contract_parity.py`
- `python scripts/api_smoke.py`

전체 실행:

```bash
pnpm verify:standard
```

## 릴리스 게이트

```bash
pnpm verify:release
```

## 화면 확인

프런트 변경 후 최소 확인 경로:

- `/overview`
- `/radar`
- `/stocks/NVDA`
- `/history?symbol=NVDA`

## 데이터 확인

- 실제 API 응답이면 출처와 신뢰도를 확인한다.
- fallback이면 화면에 `(목데이터)`가 표시되어야 한다.
- 판단 기록 저장/삭제는 `/api/research-snapshots`와 API `/snapshots` 모두 확인한다.
