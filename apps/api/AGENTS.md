# API 전용 지침

## 기술 스택
- FastAPI
- Pydantic
- 화면 단위 endpoint 구조
- 런타임 프롬프트 로더

## 라우팅 원칙
- 기능 단위보다 화면 단위를 우선한다.
- 고정 endpoint:
  - `/overview`
  - `/radar`
  - `/stocks/{symbol}`
  - `/history`

## 응답 계약
- 모든 분석 응답은 공통 envelope를 가진다.
  - `asOf`
  - `sourceRefs`
  - `missingData`
  - `confidence`
- `sourceRefs`는 아래 필드를 모두 포함한다.
  - `id`
  - `title`
  - `kind`
  - `publisher`
  - `publishedAt`
  - `url`
  - `sourceKey`
  - `symbol`
- 응답 모델은 반드시 타입으로 선언한다.

## 계약 소스 오브 트루스
- runtime JSON schema canonical source는 `packages/contracts/schemas/*.schema.json`이다.
- `apps/api/prompts/*/output.schema.json`은 호환성 복사본이며 canonical source가 아니다.
- 복사본 drift는 `python scripts/check_contract_parity.py`가 실패로 드러낸다.
- `app/services/prompt_loader.py`는 canonical contract를 우선 읽고, prompt copy는 compatibility fallback으로만 남긴다.
- prompt body는 계속 `apps/api/prompts/*/system.md`에 둔다.

## provider 원칙
- 수치, 시계열, facts는 deterministic provider가 먼저 수집한다.
- 실데이터 provider 기본값은 Alpha Vantage 기반이다.
- 요약/설명 LLM 출력은 OpenAI structured output 기준으로 다룬다.
- facts와 interpretation을 분리한다.
- 실데이터가 아직 없는 영역은 `missingData`로 명시한다.

## 프롬프트 원칙
- 공통 규칙은 `apps/api/prompts/common/` 아래에 둔다.
- 페이지별 프롬프트는 각 디렉터리 아래에 둔다.
- prompt 문자열을 Python handler에 하드코딩하지 않는다.
- JSON schema 검증과 Pydantic 검증을 모두 통과해야 응답으로 인정한다.

## 문서 규칙
- provider 구조, sourceRefs 계약, contract source of truth가 바뀌면 아래를 함께 갱신한다.
  - `apps/api/README.md`
  - `docs/changes/CHANGELOG_APPEND_ONLY.md`
  - 관련 ADR
