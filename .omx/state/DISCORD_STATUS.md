# Discord ??

- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- ?? ??: Discord ingest/relay + OMX ?? ?? ??
- meeting roles: `planner -> critic -> researcher -> architect -> executor -> verifier`
- bridge runner: `scripts/run-discord-bridge.sh`
- loop runner: `scripts/omx-loop.sh` -> `scripts/omx_autonomous_loop.py`
- quick smoke: `scripts/test-discord-bridge.sh`

## ??? ??
- `.omx/state/TEAM_CONVERSATION.jsonl`
- `.omx/state/DISCORD_INBOX.jsonl`
- `.omx/state/DISCORD_INBOX.md`
- `.omx/state/DISCORD_REPLY_STATE.json`
- `.omx/state/OMX_LOOP_STATE.json`

## ?? ??
- bridge? loop? ???? ?? ?? ?? ?? ??
- Discord ??? ???? multi-role ?? end-to-end ??
- executor ? guard/verify ??? ?? ?? ??
- ?? 3? ?? ? watchdog ?? ??
