# Discord 상태

- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- 현재 목표: Discord ingest/relay + OMX 회의 루프를 최신 지시 기준으로 안정화한다.
- meeting roles: `planner -> critic -> researcher -> architect -> executor -> verifier`
- 중요 사용자 지시 정리 파일: `.omx/state/DISCORD_IMPORTANT.md`
- bridge runner: `scripts/run-discord-bridge.sh`
- loop runner: `scripts/omx-loop.sh` -> `scripts/omx_autonomous_loop.py`
- quick smoke: `scripts/test-discord-bridge.sh`

## 읽는 상태 파일
- `.omx/state/TEAM_CONVERSATION.jsonl`
- `.omx/state/DISCORD_INBOX.jsonl`
- `.omx/state/DISCORD_INBOX.md`
- `.omx/state/DISCORD_IMPORTANT.md`
- `.omx/state/DISCORD_REPLY_STATE.json`
- `.omx/state/OMX_LOOP_STATE.json`

## 확인할 기준
- 최신 Discord 사용자 지시 1건만 소비하고 이전 미처리 지시는 다시 읽지 않는다.
- Discord 회의 응답이 역할별로 end-to-end 기록된다.
- executor 이후 guard/verify가 자동 실행된다.
- 같은 실패 3회 반복 시 watchdog이 중단과 우회책을 남긴다.
