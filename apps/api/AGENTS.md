# API 전용 지침

## 기술 스택
- FastAPI
- Pydantic
- 화면 단위 endpoint 설계
- 런타임 AI 프롬프트는 `apps/api/prompts`에 둔다

## API 설계 원칙
- endpoint는 기능 단위보다 화면 단위를 우선한다.
- 기본 묶음:
  - `/overview/*`
  - `/radar/*`
  - `/stocks/*`
  - `/history/*`
- 모든 분석 응답에는 가능한 한 아래 필드를 포함한다.
  - `asOf`
  - `sourceRefs`
  - `missingData`
  - `confidence`
- 결정론적 계산과 LLM 요약을 분리한다.
- LLM은 가격/지표/레벨/뉴스 사실을 창작하면 안 된다.

## 런타임 프롬프트 원칙
- 공통 규칙은 `apps/api/prompts/common/`에 둔다.
- 페이지별 프롬프트는 각 화면 디렉터리에 둔다.
- 각 프롬프트는 출력 JSON 스키마를 가진다.
- 코드에서 프롬프트 문자열을 하드코딩하지 말고 파일에서 로드한다.

## 점수화 엔진 원칙
- 점수 산식은 가능한 한 순수 함수와 설정 파일 기반으로 구현한다.
- 설명 문구만 LLM이 담당한다.
- 총점만 반환하지 말고 breakdown과 confidence를 함께 준다.

## 변경 시 같이 업데이트할 것
- 해당 페이지 output schema
- `docs/architecture/page-manifest.yaml`
- `docs/changes/CHANGELOG_APPEND_ONLY.md`
