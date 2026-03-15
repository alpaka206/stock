# Codex 프롬프트 운영 순서

## 원칙
- 한 번에 모든 것을 시키기보다, **기반 → 공통 → 페이지 → 문서/검증** 순서로 나눈다.
- 각 프롬프트는 아래 4가지를 포함한다.
  - 목표
  - 참고 문서
  - 제약
  - 완료 조건

## 권장 순서
1. `docs/prompts/00-레포-부트스트랩.md`
2. `docs/prompts/01-web-스캐폴딩.md`
3. `docs/prompts/02-api-스캐폴딩.md`
4. `docs/prompts/03-overview-페이지.md`
5. `docs/prompts/04-radar-페이지.md`
6. `docs/prompts/05-stock-detail-페이지.md`
7. `docs/prompts/06-history-페이지.md`
8. `docs/prompts/07-shared-contracts.md`
9. `docs/prompts/08-tests-docs-changelog.md`

## 권장 진행 방식
- 어려운 작업은 먼저 Plan 모드로 구조를 짜게 한다.
- 구현이 끝나면 review, lint, typecheck, docs update까지 한 번에 요구한다.
- 화면 구조가 바뀌면 manifest와 design-memory를 같이 갱신하게 한다.
