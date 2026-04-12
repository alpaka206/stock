# 다음 작업 지침

다음 iteration은 아래 순서를 유지한다.

1. `.omx/state/DISCORD_IMPORTANT.md`, `TASK.md`, `STATE.md`, `BACKLOG.md`, `DISCORD_STATUS.md`, `VERIFY_LAST_FAILURE.md`를 먼저 읽는다.
2. 최신 Discord 사용자 지시 1건만 처리하고, 이전 미처리 지시는 superseded로 정리한다.
3. `planner -> critic -> researcher -> architect -> executor -> verifier` 순서로 회의를 기록한다.
4. executor 이후 `scripts/no_secrets_guard.sh`와 `scripts/verify_minimal.sh`를 먼저 통과시킨다.
5. 실패 원인은 `VERIFY_LAST_FAILURE.md`와 `.omx/journal/loop-*.md`에 한국어로 남긴다.
6. 같은 실패가 3회 연속 반복되면 같은 방식 반복을 멈추고 우회책을 고른다.
7. 로컬 gate가 모두 통과한 상태이므로 다음 실제 P0는 `main 반영 -> 원격 API 재배포 확인 -> 프런트엔드 배포 URL 확인 -> 배포 사이트 브라우저 검증` 순서다.
