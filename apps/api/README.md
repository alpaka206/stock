# Stock Workspace API

`apps/api` 는 화면 단위 endpoint 와 런타임 프롬프트 로더를 가진 FastAPI 백엔드다.

## 현재 구조
- `app/main.py`: FastAPI entry
- `app/routers/*`: `/overview`, `/radar`, `/stocks/{symbol}`, `/history`
- `app/schemas/*`: Pydantic 응답 모델
- `app/services/prompt_loader.py`: 프롬프트/JSON schema 로더
- `app/services/schema_validator.py`: provider 출력 검증
- `app/services/providers/mock.py`: 개발용 mock provider
- `app/services/providers/real.py`: Alpha Vantage + OpenAI 기반 real provider
- `prompts/*`: 페이지별 system prompt 와 output schema

## 실행
```powershell
cd c:\Users\김규원\Desktop\stock\apps\api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## 환경 변수
`.env.example` 를 기준으로 설정한다.

- `STOCK_API_PROVIDER`
  - `mock`: fixture 기반 응답
  - `real`: 실데이터 + OpenAI 요약 응답
- `ALPHA_VANTAGE_API_KEY`
  - 무료 플랜 사용 가능
  - 라이선스/정책: Alpha Vantage 공식 약관 기준
- `OPENAI_API_KEY`
  - structured output 기반 요약용
- `OPENAI_MODEL`
  - 기본값: `gpt-5-mini`

## 데이터/모델 정책
- 수치와 시계열은 Alpha Vantage facts를 기반으로만 사용한다.
- LLM은 facts 해석과 한국어 요약에만 사용한다.
- sourceRefs 계약은 `id`, `title`, `kind`, `publisher`, `publishedAt`, `url`, `sourceKey`, `symbol` 로 고정한다.
- 실데이터가 없는 영역은 `missingData`에 명시한다.

## 검증
```powershell
python -m py_compile app/services/providers/mock.py app/services/providers/real.py
python -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print(client.get('/overview').status_code)"
```
