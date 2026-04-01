# Stock Workspace API

`apps/api`는 화면 단위 endpoint와 runtime prompt loader를 가진 FastAPI 백엔드다.

고정 endpoint:

- `/overview`
- `/radar`
- `/stocks/{symbol}`
- `/history`

## 실행

```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## 환경 변수

`apps/api/.env.example`를 기준으로 맞춘다.

- `STOCK_API_PROVIDER`
  - `mock`: fixture 기반 응답
  - `real`: 실데이터 + OpenAI 요약 응답
- `ALPHA_VANTAGE_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## 계약 구조

- prompt body: `apps/api/prompts/*/system.md`
- runtime JSON schema canonical source: `packages/contracts/schemas/*.schema.json`
- Pydantic 응답 모델: `app/schemas/*`
- provider 출력 검증: `app/services/schema_validator.py`
- legacy copy: `apps/api/prompts/*/output.schema.json`

`apps/api/prompts/*/output.schema.json`은 호환성 복사본이다.
canonical runtime schema는 항상 `packages/contracts/schemas/*.schema.json`을 기준으로 본다.

공통 메타 구조:

- `asOf`
- `sourceRefs`
- `missingData`
- `confidence`

## 검증

```powershell
cd apps/api
python ..\..\scripts\check_contract_parity.py
python -m py_compile app/main.py app/schemas/common.py app/schemas/overview.py app/schemas/radar.py app/schemas/stocks.py app/schemas/history.py app/services/providers/mock.py app/services/providers/real.py
python -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print(client.get('/overview').status_code, client.get('/radar').status_code, client.get('/stocks/NVDA').status_code, client.get('/history').status_code)"
```
