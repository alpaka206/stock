현재 라운드 목표
- release 성격 환경에서 원격 API cold start 때문에 `/overview` 가 500 되던 문제를 복구한다.
- `pnpm verify:automation`, `pnpm verify:standard`, `pnpm verify:release` 를 다시 통과시킨다.
- 로컬 production 웹 서버에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history` 를 직접 확인한다.

완료 조건
- 원격 API를 쓰는 production 웹 렌더링이 15초 abort 없이 열린다.
- 표준 검증 3종이 다시 모두 통과한다.
- 주요 4개 페이지가 브라우저에서 실제 콘텐츠를 렌더링한다.
