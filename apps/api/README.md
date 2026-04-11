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

## Deploy-ready hardening

- liveness는 `/health`, readiness는 `/readyz`로 분리된다.
- `/readyz`
  - `probe=config`: prompt/contracts/provider wiring과 필수 설정 표면을 점검
  - `probe=remote`: real provider 3종(Alpha Vantage, OpenDART, OpenAI)에 실제 probe를 시도
- 실배포 승인 기준은 `probe=remote`를 포함한 `pnpm verify:release` 통과다.
- API 컨테이너 배포 템플릿은 `apps/api/Dockerfile`을 사용한다.

## Free / Alternate LLM Path

- `RESEARCH_LLM_PROVIDER=auto`? ??????.
- `OPENAI_API_KEY`? ??? OpenAI? ?? ?????.
- `OPENAI_API_KEY`? ?? `GEMINI_API_KEY`? ??? Gemini? ?????.
- ? ?? ?? ??? provider ??? ???? `/overview`, `/radar`, `/stocks/{symbol}`, `/history`? deterministic summary? degrade ???.

?? env:

- `RESEARCH_LLM_PROVIDER` = `auto` | `openai` | `gemini` | `none`
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (?? `gemini-2.5-flash`)
- `GEMINI_BASE_URL` (?? Google Generative Language API endpoint)
