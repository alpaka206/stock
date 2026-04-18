현재 사실
- 작업 브랜치는 `issue/134-research-api-ipv6-loopback` 이다.
- 브랜치는 `origin/develop_loop`의 현재 head `33ba7b8cf3d54ac7bd29b7f3b69b447bf6d18645` 기준으로 새로 만들었다.
- PR #133은 merged/closed 상태이고, 이슈 #134는 `apps/web/lib/server/research-api.ts`의 `[::1]` 로컬 판정 보완과 회귀 테스트 1건으로 범위가 고정돼 있다.
- PR #135는 `issue/131-최상위-계약-primary-task -> develop_loop` 로 아직 open 상태라서, 이번 이슈는 그 브랜치와 분리해 진행한다.

최근 검증 결과
- `git fetch origin --prune` 후 `origin/develop_loop` 가 `33ba7b8cf3d54ac7bd29b7f3b69b447bf6d18645` 임을 확인했다.
- GitHub 확인: PR #133 merged, PR #135 open, issue #134 open.
- `git switch -c issue/134-research-api-ipv6-loopback origin/develop_loop` 가 성공했고 작업 트리는 clean 상태를 유지했다.

남은 리스크
- `[::1]` 케이스 보완 코드와 회귀 테스트는 아직 적용 전이다.
- 웹 전용 테스트를 어느 기존 게이트에 연결할지 아직 확정하지 않았다.
- 현재 브랜치 upstream 이 `origin/develop_loop` 로 잡혀 있어 첫 push 때 새 원격 브랜치 업스트림을 명시해야 한다.

다음 우선순위
- `apps/web/lib/server/research-api.ts` 에 `[::1]` local hostname 판정을 추가한다.
- 같은 케이스를 고정하는 회귀 테스트 1건을 추가하고 기존 검증 경로에 연결한다.
- 최소 검증(`pnpm lint:web`, 관련 테스트/타입체크) 후 issue branch PR을 만든다.
