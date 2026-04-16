# 다음 작업 지침

현재 최상위 목표는 `AGENTS.md` 의 `PRIMARY_TASK` 와 `MIN_EXIT_CONDITION` 이다.
다음 세션은 목표 자체를 다시 쓰지 말고, 아래 순서대로 바로 실행한다.

1. 실제 Discord 채널에서 허용 사용자 메시지 1건을 보내고, ingest -> 회의 -> 회신 -> `.omx/state/TEAM_CONVERSATION.jsonl` 기록까지 확인한다.
2. `/overview`, `/radar` 초기 지연을 배포 환경 기준으로 다시 재현하고, 코드와 설정 기준으로 원인을 줄인 뒤 재검증한다.
3. 현재 자동화 변경을 issue-linked branch 기준으로 정리해서 GitHub 자동 issue -> branch -> PR -> develop 흐름을 다시 연다.
4. 프런트와 백엔드 배포 URL의 핵심 경로를 다시 확인하고, 결과와 남은 리스크를 `.omx/state/STATE.md` 와 `.omx/journal/` 에 한국어로 기록한다.

## 재확인할 기준

- Discord: 실제 사용자 메시지 1건, latest-only 처리, superseded 정리, 역할별 응답, 로컬 로그 보존
- 프런트: `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`
- 백엔드: `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`, `/news`, `/calendar`
- 명령: `pnpm verify:automation`, `pnpm verify:standard`

## 시작 메모

- 로컬 Discord 상태 로그는 비워 둔 상태다.
- 다음 실행은 새 Discord 메시지 1건을 기준으로 시작하면 된다.
