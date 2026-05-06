현재 라운드 목표
- PR #135를 `origin/develop_loop` 기준으로 리베이스하고 충돌을 정리한다.
- PR #135를 `develop_loop`에 반영한 뒤, PR #155(`develop_loop -> develop`)가 최신 변경을 포함하도록 갱신한다.
- Dependabot 실패 PR 중 호환 가능한 변경은 이미 반영된 상태로 정리하고, ESLint 10 PR #151은 호환성 사유를 남긴다.

완료 조건
- PR #135 브랜치의 리베이스가 끝나고 검증 명령이 통과한다.
- PR #135가 `develop_loop`에 병합된다.
- PR #155가 최신 `develop_loop` 변경을 포함하고 `develop` 병합 가능 상태가 된다.
- Dependabot PR 정리 결과가 GitHub PR 댓글이나 종료 상태로 남는다.
