현재 사실
- 브랜치는 `issue/131-최상위-계약-primary-task` 이다.
- `develop_loop` 대상 PR #132 가 생성됐고 auto-merge 가 활성화됐다.
- PR #133은 이미 merge 된 닫힌 PR이며, 남아 있던 review thread 1건도 `resolved=true`, `outdated=true` 상태로 확인됐다.
- PR #133 후속 구현은 다시 열지 않고, `[::1]` bracketed IPv6 loopback 로컬 판정 보완은 별도 이슈 #134 로 분리했다.
- 자동화 검증, 표준 검증, release 검증이 모두 통과했다.
- 원격 API를 직접 붙인 release 성격 환경에서 15초 타임아웃으로 `/overview` 가 500 되던 문제를 재현했고 수정했다.
- 수정 후 로컬 production 웹 서버에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history` 가 모두 실제 콘텐츠를 렌더링했다.

최근 검증 결과
- `pnpm verify:automation` 통과
- `pnpm verify:standard` 통과
- `pnpm verify:release` 통과
- `next start -p 3001` 기준 브라우저 확인 통과
  - `/overview`
  - `/radar`
  - `/stocks/NVDA`
  - `/history`
- GitHub 확인: PR #133 `merged=true`, 남은 review thread 1건은 `resolved=true`, `outdated=true`
- GitHub 확인: 후속 hardening 이슈 #134 생성 (`fix: [::1] research API 로컬 판정 보완`)

남은 리스크
- `apps/web/lib/server/research-api.ts` 는 아직 `[::1]` hostname 을 local 로 판정하지 못해 release 모드에서 로컬 호출이 remote timeout 경로로 오분류될 수 있다.
- 외부에 실제 배포된 프런트 URL은 저장소 안에서 명시적으로 찾지 못했다.
- `stock-front.vercel.app` 후보는 현재 저장소 UI와 일치하지 않아 배포 프런트 직접 확인 근거로 쓰기 어렵다.
- 실제 호스팅 콘솔 접근 없이 프로덕션 프런트 배포 상태를 최종 단정하기는 어렵다.

다음 우선순위
- 이슈 #134 기준 새 issue 브랜치를 만들어 `research-api.ts` 의 `[::1]` 로컬 판정 보완과 회귀 테스트 1건을 최소 범위로 구현한다.
- PR #132 CI 상태를 지켜보고 green 이면 자동 머지를 확인한다.
- 외부 배포 프런트 URL을 확인할 수 있으면 같은 4개 경로를 다시 직접 점검한다.
