현재 라운드 목표
- 이슈 #159 기준으로 핵심 화면 `/overview`, `/radar`, `/stocks/[symbol]`, `/history`의 브라우저 E2E 검증을 추가한다.
- E2E 실행 중 발견된 hydration mismatch를 같은 브랜치에서 복구한다.
- 변경사항을 커밋하고 `develop` 대상 PR로 올린다.

완료 조건
- `pnpm test:e2e -- --project=chromium`이 7개 시나리오 모두 통과한다.
- `pnpm verify:automation`과 `pnpm verify:standard`가 통과한다.
- Radar preset 날짜가 서버와 브라우저에서 같은 문자열로 렌더링된다.
- 브랜치 `issue/159-core-pages-e2e`가 원격에 push되고 `develop` 대상 PR이 생성된다.
