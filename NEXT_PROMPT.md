1. `pnpm verify:standard`를 실행하고 실패한 lint/typecheck/build를 수정한다.
2. 프런트 PR #196의 `verify`, `codeql (javascript-typescript)`, `dependency-review` 상태를 확인하고 통과하면 squash 없이 develop에 병합한다.
3. PR merge 후 branch protection required checks에서 삭제된 Python CodeQL 체크가 남아 있으면 제거한다.
4. Spring 백엔드가 켜진 상태에서 `pnpm verify:release`를 실행한다.
5. 다음 기능은 백엔드 ingest worker와 실제 provider 저장 흐름부터 진행한다.
