현재 라운드 목표
- 이슈 #161 기준으로 리서치 스냅샷을 localStorage 전용에서 API 동기화 가능한 영속 저장 흐름으로 확장한다.
- 저장, 조회, 삭제가 API smoke와 브라우저 E2E에서 관측되도록 검증을 추가한다.
- 변경사항을 커밋하고 `develop` 대상 PR로 올린다.

완료 조건
- API `/snapshots` GET/POST/DELETE가 동작한다.
- 웹 `/api/research-snapshots` 프록시가 backend snapshots API와 연결된다.
- 종목 상세에서 저장한 스냅샷이 히스토리 화면에서 다시 보인다.
- `pnpm test:e2e -- --project=chromium`, `pnpm verify:automation`, `pnpm verify:standard`가 통과한다.
