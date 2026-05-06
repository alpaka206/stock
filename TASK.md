현재 라운드 목표
- 현재 이슈 브랜치의 미커밋 변경사항을 안전하게 정리해 `develop_loop`로 올린다.
- 실패 중인 Dependabot PR들의 의존성 변경을 정책 흐름에 맞게 이슈 브랜치에 배치 반영한다.
- `develop_loop -> develop` 승격이 가능하도록 검증 결과와 남은 예외를 문서에 남긴다.

완료 조건
- 이슈 브랜치 커밋이 `origin/develop_loop` 기준으로 정리되어 PR 생성 가능한 상태가 된다.
- Dependabot 업데이트 중 CI 호환 가능한 항목은 lockfile까지 반영된다.
- 웹 lint, typecheck, build, npm audit 결과가 관측 가능하게 남는다.
- `STATE.md`와 `NEXT_PROMPT.md`에 남은 리스크와 다음 액션이 한국어로 기록된다.
