# 작업 계약

- PRIMARY_TASK: 1단계 Discord 기반 agent 회의형 자동화 완성. 2단계 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 를 중심으로 주식 데이터·API·FE·BE 기능 완성. 3단계 QA, GitHub 흐름, 배포, 실배포 확인까지 마무리. 4단계 남은 리스크와 후속 기능을 문서와 저널에 기록.
- MIN_EXIT_CONDITION: 허용된 Discord 사용자 메시지 1건이 최신 트리거로만 처리되고 역할별 응답이 실제 Discord와 `.omx/state/TEAM_CONVERSATION.jsonl` 에 남는다. `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 와 핵심 기능이 end-to-end 로 검증된다. `pnpm verify:standard` 와 release 검증, 배포 사이트 직접 확인이 끝난다.
- AUTO_CONTINUE_POLICY: 최소 종료 조건을 충족할 때까지 가장 작고 검증 가능한 다음 작업을 스스로 고르고 계속 진행
- RELEASE_TO_MAIN_POLICY: auto-merge-if-green
- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- MULTI_AGENT_CONSENSUS: `planner -> critic -> researcher -> architect -> executor -> verifier`

## 현재 라운드 목표

1. 실제 Discord 채널에서 사용자 메시지 1건 기준 ingest -> 회의 -> 회신 루프를 검증한다.
2. `/overview`, `/radar` 초기 지연과 핵심 경로 안정성을 다시 확인한다.
3. issue-linked branch 기준 GitHub 자동 흐름을 다시 열 수 있는 상태로 정리한다.

## 현재 라운드 완료 조건

- `pnpm verify:automation` 과 `pnpm verify:standard` 가 통과한다.
- 실제 Discord 메시지 1건으로 역할 응답과 로컬 로그가 남는 운영 기록이 남는다.
- `/overview`, `/radar`, `/stocks/NVDA`, `/history` 기준으로 현재 리스크와 다음 액션이 `STATE.md` 와 저널에 기록된다.

## 메모

- 로컬 Discord 상태 로그는 한 번 비운 상태에서 다시 시작한다.
- 다음 세션은 새 Discord 메시지 1건으로 바로 실물 검증을 시작하면 된다.
