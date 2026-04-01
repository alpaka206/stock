# `@stock/contracts`

금융 리서치 워크스페이스의 공통 계약 패키지다.

- 단일 runtime JSON schema 소스: `schemas/*.schema.json`
- web TypeScript 타입 소스: `src/index.ts`
- API prompt loader 는 이 패키지의 schema 를 읽어 LLM structured output 과 provider validation 에 함께 사용한다.

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
