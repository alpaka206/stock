# TASK

## 현재 라운드 목표

1. 실제 Discord 메시지 1건 기준으로 ingest -> 회의 -> 회신 -> 로그 기록까지 검증한다.
2. `/overview`, `/radar` 초기 지연과 핵심 경로 안정성을 다시 확인한다.
3. issue-linked branch 기준 GitHub 자동 흐름을 다시 열 수 있는 상태로 정리한다.

## 현재 라운드 완료 조건

- `pnpm verify:automation` 이 통과한다.
- `pnpm verify:standard` 가 통과한다.
- 실제 Discord 메시지 1건으로 역할 응답과 `.omx/state/TEAM_CONVERSATION.jsonl` 기록이 남는다.
- `/overview`, `/radar`, `/stocks/NVDA`, `/history` 기준 현재 리스크와 다음 액션이 `STATE.md` 와 저널에 기록된다.
