# 목표
웹과 API 사이에서 공통으로 쓰는 계약(contract)을 정리한다.

# 할 일
- `packages/contracts` 를 만들고 화면별 응답 타입을 정리한다.
- overview / radar / stock detail / history 응답 타입을 분리한다.
- `asOf`, `sourceRefs`, `missingData`, `confidence` 공통 메타 구조를 만든다.
- score breakdown 구조를 공통 타입으로 만든다.

# 완료 조건
- 웹과 API 모두 공통 타입을 참조한다.
- 런타임 프롬프트 output schema 와 계약이 일치한다.
