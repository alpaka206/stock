# 목표
web과 api가 같은 계약을 따르도록 공통 계약 구조를 정리한다.

# 참고 문서
- docs/architecture/workspace-blueprint.md
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- apps/web/AGENTS.md
- apps/api/AGENTS.md

# 할 일
- `packages/contracts` 또는 이에 준하는 공통 계약 폴더를 만든다.
- JSON schema 또는 계약 파일을 단일 소스로 정한다.
- overview / radar / stocks / history 응답 계약을 정리한다.
- `asOf`, `sourceRefs`, `missingData`, `confidence`, `score breakdown` 공통 메타 구조를 명시한다.
- web 타입, API Pydantic schema, prompt output schema가 어긋나면 정리한다.

# 제약
- Python과 TypeScript를 무리하게 한 런타임으로 합치지 않는다.
- 프롬프트 문자열을 코드에 하드코딩하지 않는다.
- fabricated 데이터 없이 계약과 출처 구조를 먼저 맞춘다.

# 완료 조건
- 공통 계약 단일 소스가 생긴다.
- web과 api가 같은 계약을 따르도록 정리된다.
- 문서와 changelog, 필요한 ADR이 갱신된다.
