1. PR #135 리베이스 충돌을 모두 해결하고 `git rebase --continue`를 완료한다.
2. PR #135 브랜치에서 lint, typecheck, build, audit, 관련 자동화 테스트를 실행한다.
3. PR #135 브랜치를 push하고 GitHub checks를 확인한 뒤 `develop_loop`에 병합한다.
4. PR #155(`develop_loop -> develop`)가 최신 `develop_loop` 변경을 포함하는지 확인하고 병합 가능 상태로 정리한다.
5. Dependabot PR 정리 댓글과 ESLint 10 보류 사유를 GitHub에 남긴다.
