현재 사실
- `develop` 최신 커밋 `97f9f87` 기준으로 브랜치 `issue/159-core-pages-e2e`에서 작업 중이다.
- 루트에 Playwright 설정과 `tests/e2e/core-pages.spec.ts`가 추가되었다.
- E2E는 API가 없어도 fixture fallback으로 핵심 화면을 검증하도록 `STOCK_API_BASE_URL`을 비우고 `RESEARCH_ALLOW_FIXTURE_FALLBACK=true`로 dev server를 띄운다.
- `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`에 안정적인 E2E 테스트 훅을 추가했다.
- Radar preset 날짜 포맷은 `Intl.DateTimeFormat` 대신 ISO 문자열 기반 고정 포맷을 사용해 서버/브라우저 hydration mismatch를 제거했다.

최근 검증 결과
- `pnpm test:e2e -- --project=chromium`: 7개 시나리오 통과.
- `pnpm verify:automation`: 통과.
- `pnpm verify:standard`: 통과.
- 표준 검증 안에서 text quality, automation, web lint, web typecheck, web build, contract parity, API py_compile, API smoke가 모두 통과했다.

남은 리스크
- E2E는 현재 Chromium desktop 단일 프로젝트이며 모바일 viewport와 접근성 검증은 아직 없다.
- Playwright 테스트는 fixture fallback 흐름을 사용하므로 실제 배포 API 연결 검증은 release 검증에서 별도로 수행해야 한다.
- Next dev server가 route transition 중 `scroll-behavior: smooth` 경고를 출력하지만 테스트 실패 조건은 아니다.

다음 우선순위
- 현재 변경사항을 `test: 핵심 화면 E2E 검증 추가` 커밋으로 정리한다.
- 브랜치를 원격에 push하고 `develop` 대상 PR을 생성한다.
- PR checks 통과 후 auto-merge를 설정한다.
- 다음 브랜치에서는 이슈 #161 리서치 스냅샷 영속 저장소를 구현한다.
