# 목표

Next.js 프런트와 Spring Boot 백엔드가 같은 계약을 따르도록 공통 계약 구조를 정리한다.

# 참고 문서
- docs/architecture/workspace-blueprint.md
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- apps/web/AGENTS.md
- ../stock_BE/AGENTS.md

# 할 일
- `packages/contracts` 또는 이에 준하는 공통 계약 폴더를 만든다.
- JSON schema 또는 계약 파일을 단일 소스로 정한다.
- overview / radar / stocks / history 응답 계약을 정리한다.
- `asOf`, `sourceRefs`, `missingData`, `confidence`, `score breakdown` 공통 메타 구조를 명시한다.
- web 타입, Spring DTO, OpenAPI 문서가 어긋나면 정리한다.

# 제약
- 백엔드 DB 구조를 프런트 타입에 직접 노출하지 않는다.
- 추후 LLM worker를 붙일 때도 동일 schema를 검증 기준으로 쓴다.
- fabricated 데이터 없이 계약과 출처 구조를 먼저 맞춘다.

# 완료 조건
- 공통 계약 단일 소스가 생긴다.
- web과 Spring 백엔드가 같은 계약을 따르도록 정리된다.
- 문서와 changelog, 필요한 ADR이 갱신된다.
