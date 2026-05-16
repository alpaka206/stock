# `@stock/contracts`

금융 리서치 워크스페이스의 공통 계약 패키지다.

- 단일 runtime JSON schema 소스: `schemas/*.schema.json`
- web TypeScript 타입 소스: `src/index.ts`
- Spring 백엔드 응답과 Next.js 프런트 타입은 이 패키지의 계약을 기준으로 맞춘다.
- 추후 LLM 요약 worker를 붙일 때도 이 schema를 structured output 검증 기준으로 사용한다.

현재 범위:

- `overview`
- `radar`
- `stocks`
- `history`
- 공통 메타 구조
  - `asOf`
  - `sourceRefs`
  - `missingData`
  - `confidence`
  - `score breakdown`
