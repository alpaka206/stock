# NEXT PROMPT

1. 실제 Discord 채널에서 허용 사용자 메시지 1건을 보내고 latest-only 처리, superseded 정리, 역할별 응답, `.omx/state/TEAM_CONVERSATION.jsonl` 기록까지 확인한다.
2. 루프 1번째 시작일 때만 한 명의 agent가 `작업을 시작합니다.` 를 Discord에 보내는지 확인한다.
3. `/overview` 와 `/radar` 초기 지연을 배포 환경 기준으로 다시 재현하고, 코드 또는 설정 원인을 줄인 뒤 재검증한다.
4. `pnpm verify:automation` 과 `pnpm verify:standard` 를 실행하고 실패 시 최우선으로 복구한다.
5. issue 생성 -> issue-linked branch 생성 -> 작업 커밋 -> issue branch -> `develop` PR 자동 merge -> `develop -> main` PR 생성 및 Discord 보고 흐름을 다시 확인한다.
