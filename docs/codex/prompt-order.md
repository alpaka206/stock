# Codex 프롬프트 운영 순서

## 원칙

- 한 번에 모든 기능을 끝내려 하지 말고 화면, API, 문서, 검증을 작은 단위로 나눈다.
- 각 프롬프트는 목표, 참고 문서, 제약, 완료 조건을 포함한다.
- 변경 후에는 `page-manifest.yaml`, `component-manifest.yaml`, `design-memory.md`를 함께 갱신한다.
- 사용자가 보는 문구는 개발자 설명이 아니라 실제 서비스 문장으로 작성한다.

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
10. `docs/prompts/09-완성형-주식-분석-사이트.md`

## 진행 방식

- 화면 구현은 실제 데이터 연동을 우선하고, 대체 데이터는 반드시 `(목데이터)`로 표시한다.
- 서버가 관리해야 하는 값은 브라우저 저장소에 장기 보관하지 않는다.
- 검증은 `pnpm verify:standard`를 기본 게이트로 사용한다.
- 브랜치 흐름은 issue branch에서 `develop` PR로 올리고, `develop -> main`은 별도 release PR로 만든다.
