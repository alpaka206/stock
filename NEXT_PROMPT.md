1. `pnpm verify:standard`를 실행하고 실패한 lint/typecheck/build를 수정한다.
2. `stock_BE` PR #6의 `verify`, `codeql`, `dependency-review` 상태를 확인하고 통과하면 squash 없이 develop에 병합한다.
3. 프런트 브랜치 `refactor/189-use-spring-backend`를 push하고 develop 대상 PR을 연다.
4. PR merge 후 branch protection required checks에서 삭제된 Python CodeQL 체크가 남아 있으면 제거한다.
5. 다음 기능은 백엔드 ingest worker와 실제 provider 저장 흐름부터 진행한다.
