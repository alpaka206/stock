# API 전용 지침

## 기술 스택
- FastAPI
- Pydantic
- 화면 단위 endpoint 구조
- 런타임 프롬프트 로더

## 엔드포인트 원칙
- 기능 단위보다 화면 단위를 우선한다.
- 기본 endpoint 묶음:
  - `/overview`
  - `/radar`
  - `/stocks/{symbol}`
  - `/history`

## 응답 계약
- 모든 분석 응답은 아래 공통 envelope 를 가진다.
  - `asOf`
  - `sourceRefs`
  - `missingData`
  - `confidence`
- `sourceRefs` 는 아래 필드를 모두 포함한다.
  - `id`
  - `title`
  - `kind`
  - `publisher`
  - `publishedAt`
  - `url`
  - `sourceKey`
  - `symbol`
- 응답 모델은 반드시 타입으로 선언한다.

## provider 원칙
- 수치, 시계열, facts 는 deterministic provider 에서 먼저 수집한다.
- 기본 실데이터 provider 는 Alpha Vantage 를 기준으로 둔다.
- 요약/해석 LLM 호출은 OpenAI structured output 기준으로 둔다.
- facts 와 interpretation 을 분리한다.
- 실데이터가 아직 없는 영역은 `missingData` 로 명시한다.

## 프롬프트 원칙
- 공통 규칙은 `apps/api/prompts/common/` 아래에 둔다.
- 페이지별 프롬프트는 각 화면 디렉터리 아래에 둔다.
- 각 프롬프트는 대응하는 출력 JSON schema 를 가진다.
- 프롬프트 문자열을 코드에 하드코딩하지 않는다.

## 문서 규칙
- provider 구조나 sourceRefs 계약이 바뀌면 아래를 함께 갱신한다.
  - `apps/api/README.md`
  - `docs/changes/CHANGELOG_APPEND_ONLY.md`
  - 관련 ADR
