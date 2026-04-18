현재 사실
- PR #154는 `issue/134-research-api-ipv6-loopback -> develop_loop`로 생성되었고 squash merge로 `develop_loop`에 반영되었다.
- PR #155(`develop_loop -> develop`)는 열려 있으며, PR #135를 먼저 반영해야 최신 작업을 모두 포함할 수 있다.
- PR #135는 `issue/131-최상위-계약-primary-task -> develop_loop`이며 오래된 브랜치지만 release timeout, OMX write gate, 운영 문서 변경이 남아 있다.
- PR #135 리베이스 중 오래된 문서 상태 충돌은 최신 작업 흐름 기준으로 정리하고 있다.
- PR #133 후속 review thread 확인과 `[::1]` 로컬 판정 보완은 이미 PR #154에 포함된 현재 상태와 맞춰 정리한다.
- Dependabot 호환 업데이트는 PR #154에 묶어 반영했다. ESLint 10 PR #151은 현재 React ESLint 플러그인 생태계와 맞지 않아 별도 보류가 필요하다.

최근 검증 결과
- PR #154 반영 전 `pnpm --dir apps/web lint`, `typecheck`, `build`, `audit --audit-level moderate`가 통과했다.
- `uv run` 기반 자동화 스크립트, Discord bridge 관련 테스트, API smoke, release readiness 검증이 통과했다.
- release readiness에서 `/readyz`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`, `/instruments/search?q=nvda`가 200 JSON 응답을 반환했다.
- PR #135의 원래 작업에서는 `pnpm verify:automation`, `pnpm verify:standard`, `pnpm verify:release` 및 로컬 production 웹 확인이 통과한 기록이 있다.

남은 리스크
- PR #135 리베이스 중 추가 충돌이 발생할 수 있다.
- PR #155는 `develop_loop`가 `develop`보다 뒤처진 상태로 표시될 수 있으므로 병합 방식 선택이 필요하다.
- ESLint 10은 현재 `eslint-plugin-react` 호환성 문제로 바로 올리면 lint가 깨진다.

다음 우선순위
- PR #135 리베이스를 끝내고 관련 검증을 실행한다.
- PR #135를 `develop_loop`에 병합한다.
- PR #155를 최신 상태로 확인하고 `develop` 반영 경로를 정리한다.
- Dependabot PR에 배치 반영 여부와 ESLint 10 보류 사유를 남긴다.
