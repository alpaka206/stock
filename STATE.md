현재 사실
- 현재 작업 브랜치는 `issue/134-research-api-ipv6-loopback` 이고 원격 tracking branch는 삭제된 상태다.
- 원격 `develop_loop`에는 기존 #134 커밋이 이미 PR #136/#137을 통해 반영되어 있으며, 현재 브랜치의 기존 커밋과 tree는 같은 상태였다.
- 이번 라운드의 새 변경은 overview/shell 리디자인, 종목 통합 검색 API, 리서치 스냅샷 저장 UI, i18n 정리, Dependabot 의존성 배치 업데이트다.
- 열린 Dependabot PR들은 `main` 대상으로 생성되어 release guard 정책에 막혀 있었다.
- Dependabot 웹 PR들의 `verify`와 `dependency-review` 실패는 package manifest만 바뀌고 `pnpm-lock.yaml`이 갱신되지 않은 것이 공통 원인이었다.
- ESLint 10 업데이트(PR #151)는 현재 `eslint-plugin-react` 최신 버전이 ESLint 10 peer/API를 지원하지 않아 lint를 깨뜨린다. 이번 배치에서는 ESLint를 9.39.4로 유지한다.

최근 검증 결과
- `pnpm --dir apps/web lint` 통과.
- `pnpm --dir apps/web typecheck` 통과.
- `pnpm --dir apps/web build` 통과.
- `pnpm --dir apps/web audit --audit-level moderate` 통과. `postcss`와 `ip-address` 경고는 root `pnpm.overrides`로 해소했다.
- `uv run` 기반 개별 자동화 검증 통과: ralph setup, OMX contract parsing, release PR policy, verifier output, Discord mode/control/latest-only, ralph runtime, executor write gate, no secrets guard, Discord bridge smoke.
- API 검증 통과: contract parity, API py_compile, API smoke.
- release readiness 통과. `/readyz`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`, `/instruments/search?q=nvda`가 200 JSON 응답을 반환했다.

남은 리스크
- `pnpm verify:automation`과 `pnpm verify:standard` 래퍼는 로컬 `python`이 Microsoft Store shim이라 직접 실행하면 깨진다. 같은 하위 스크립트들은 `uv run`으로 개별 실행해 통과를 확인했다.
- TypeScript 6.0.3은 typecheck/build는 통과했지만 `eslint-config-next` 내부 `typescript-eslint` peer 경고가 남는다. 현재는 경고이며 lint 실패는 아니다.
- 브랜치는 `origin/develop_loop` 위로 rebase됐고 기존 #134 cherry-pick 커밋 2개는 건너뛰어졌다.
- Dependabot PR #151은 호환 가능한 plugin 생태계가 나오기 전까지 닫거나 보류 코멘트가 필요하다.

다음 우선순위
- 이슈 브랜치를 원격에 push하고 `develop_loop` 대상 PR을 만든다.
- PR 생성 후 Dependabot PR #138, #139, #140, #145, #148, #149, #150, #152, #153은 배치 반영 사실을 코멘트하고 정리한다.
- #151은 ESLint 10 호환성 문제를 코멘트하고 보류 또는 close 처리한다.
- `develop_loop` 반영 뒤 `develop_loop -> develop` 승격 PR을 준비한다.
