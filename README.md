# AI 주식 리서치 워크스페이스

뉴스, 차트, 섹터, 수급, 옵션/공매도, 점수, 과거 이벤트를 한 흐름 안에서 읽는 모노레포다.

고정 메인 화면:

1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

## 저장소 구조

- `apps/web`: Next.js App Router 프론트엔드
- `apps/api`: FastAPI 백엔드
- `packages/contracts`: 공통 JSON schema / TypeScript 계약 패키지
- `docs`: architecture manifest, design memory, ADR, changelog, Codex prompt 문서
- `scripts`: 검증 및 보조 스크립트

## 먼저 읽을 문서

- `AGENTS.md`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/codex/prompt-order.md`

## 실행

### web

루트에서:

```powershell
pnpm install
pnpm dev:web
```

브라우저:

- `http://localhost:3000/overview`
- `http://localhost:3000/radar`
- `http://localhost:3000/stocks/NVDA`
- `http://localhost:3000/history`

### api

```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

환경 변수는 `apps/api/.env.example`를 기준으로 맞춘다.

## 검증

```powershell
pnpm lint:web
pnpm typecheck:web
pnpm build:web
pnpm check:contracts
python -m py_compile apps/api/app/main.py apps/api/app/schemas/common.py apps/api/app/schemas/overview.py apps/api/app/schemas/radar.py apps/api/app/schemas/stocks.py apps/api/app/schemas/history.py apps/api/app/services/providers/mock.py apps/api/app/services/providers/real.py
```

FastAPI mock smoke 예시:

```powershell
python -c "import sys; sys.path.insert(0, r'apps/api'); from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print(client.get('/overview').status_code, client.get('/radar').status_code, client.get('/stocks/NVDA').status_code, client.get('/history').status_code)"
```

## 계약 원칙

- runtime JSON schema 단일 소스는 `packages/contracts/schemas/*.schema.json`
- web 타입은 `packages/contracts/src/index.ts`를 기준으로 참조
- API prompt body는 `apps/api/prompts/*/system.md`
- `apps/api/prompts/*/output.schema.json`은 호환성 복사본이며 canonical source가 아니다
- drift 검증은 `python scripts/check_contract_parity.py`

## 데이터 신뢰 원칙

- 출처 없는 가격, 뉴스, 레벨, 점수는 만들지 않는다
- 숫자와 시계열은 provider가 결정론적으로 계산한다
- 실데이터가 없으면 `missingData` 또는 unavailable 상태로 드러낸다
- web 화면은 live / mock / fixture 상태를 배지로 노출한다
