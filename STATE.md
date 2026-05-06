현재 사실
- PR #154는 `issue/134-research-api-ipv6-loopback -> develop_loop`로 생성되었고 squash merge로 `develop_loop`에 반영되었다.
- PR #135는 `issue/131-최상위-계약-primary-task -> develop_loop`로 재정렬했고 GitHub checks 통과 후 `develop_loop`에 병합되었다.
- PR #155(`develop_loop -> develop`)는 PR #135와 PR #154 변경을 모두 포함한다.
- PR #155의 GitHub checks는 통과했고 auto-merge가 REBASE 방식으로 설정되어 있다.
- PR #155는 현재 `REVIEW_REQUIRED` 보호 규칙 때문에 자동 병합 대기 중이다.
- Dependabot 중복 PR #138, #139, #140, #145, #148, #149, #150, #152, #153은 PR #154에 배치 반영됐다는 댓글을 남기고 닫았다.
- Dependabot PR #151은 ESLint 10.3.0이 현재 Next/React lint 스택과 호환되지 않아 보류 사유를 남기고 닫았다.

최근 검증 결과
- PR #154 반영 전 `pnpm --dir apps/web lint`, `typecheck`, `build`, `audit --audit-level moderate`가 통과했다.
- `uv run` 기반 자동화 스크립트, Discord bridge 관련 테스트, API smoke, release readiness 검증이 통과했다.
- release readiness에서 `/readyz`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`, `/instruments/search?q=nvda`가 200 JSON 응답을 반환했다.
- PR #135 리베이스 후 `pnpm install --frozen-lockfile --store-dir .pnpm-store`, `pnpm --dir apps/web lint`, `typecheck`, `build`, `audit --audit-level moderate`, executor write gate 테스트, ralph setup 검증, text quality guard가 통과했다.
- PR #155 GitHub checks는 verify, dependency-review, CodeQL, Vercel 상태가 통과했다.

남은 리스크
- PR #155는 리뷰 요구 조건이 충족되기 전까지 `develop`에 자동 병합되지 않는다.
- ESLint 10은 현재 `eslint-plugin-react` 호환성 문제로 바로 올리면 lint가 깨진다.
- PR #155가 병합된 뒤에는 `develop` 기준으로 넓은 검증을 다시 확인해야 한다.

다음 우선순위
- PR #155에 필요한 리뷰 승인 조건을 충족한다.
- auto-merge가 `develop`에 반영됐는지 확인한다.
- `develop` 반영 후 `pnpm verify:automation`, `pnpm verify:standard`, release 검증 상태를 다시 확인한다.
- 이후 `develop -> main` release PR이 필요하면 수동 merge 정책을 지키며 생성하고 Discord에 보고한다.
