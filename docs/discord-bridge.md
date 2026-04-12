# Discord Bridge

## Current Status
- bridge is now an ingest and relay layer, not a canned auto-replier
- real runtime reads `omx_discord_bridge/.env.discord` by default
- secret values are never printed or committed
- bridge forwards `/event` payloads to the Discord webhook when the env file exists
- bridge polls Discord replies from the configured parent channel and stores them in repo-local logs
- `scripts/omx-loop.sh` drives the real multi-role meeting flow through `omx exec`

## Files
- `omx_discord_bridge/discord_omx_bridge.py`
- `omx_discord_bridge/requirements.txt`
- `omx_discord_bridge/.env.example`
- `scripts/run-discord-bridge.sh`
- `scripts/omx-loop.sh`
- `scripts/omx_autonomous_loop.py`
- `scripts/omx_role_output.schema.json`
- `scripts/check-discord-bridge.sh`
- `scripts/test-discord-bridge.sh`
- `scripts/sync-discord-replies.sh`

## Shared Logs
- `.omx/state/TEAM_CONVERSATION.jsonl`
- `.omx/state/DISCORD_INBOX.jsonl`
- `.omx/state/DISCORD_INBOX.md`
- `.omx/state/DISCORD_REPLY_STATE.json`
- `.omx/state/OMX_LOOP_STATE.json`
- `.omx/runtime/discord-bridge-status.json`

## Runtime Model
1. `scripts/run-discord-bridge.sh` keeps the local bridge alive.
2. `scripts/omx-loop.sh` runs forever when `INFINITE_MODE=true` or `MAX_ITERATIONS=0`.
3. New Discord user messages are imported into `.omx/state/DISCORD_INBOX.jsonl` and `.omx/state/TEAM_CONVERSATION.jsonl`.
4. The loop selects the next trigger from Discord input, verify failures, or the top P0 backlog item.
5. `planner -> critic -> researcher -> architect -> executor -> verifier` are run through `omx exec`.
6. Every role message and the closing summary are posted back to Discord and also logged locally when bridge fallback is used.
7. After `executor`, the loop runs `scripts/no_secrets_guard.sh` and `scripts/verify_minimal.sh`.

## Suggested Launch
```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/run-discord-bridge.sh
$env:INFINITE_MODE='true'
& 'C:\Program Files\Git\bin\bash.exe' scripts/omx-loop.sh
```

## Fast Bridge Smoke Test
```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/check-discord-bridge.sh
& 'C:\Program Files\Git\bin\bash.exe' scripts/test-discord-bridge.sh
```

Expected result:
- `/health` returns JSON with runtime bridge status
- one smoke message per role reaches Discord
- `/sync-replies` returns JSON

## Read Path
- if you type in the configured Discord channel and your user ID is in `ALLOWED_DISCORD_USER_IDS`, the bridge imports the message into `.omx/state/DISCORD_INBOX.jsonl`
- imported messages are also appended to `.omx/state/TEAM_CONVERSATION.jsonl`
- the loop reads those files, holds an actual repo-aware meeting, and posts the discussion back to Discord
- autonomous internal meetings are also written to Discord and the local journal

## Security
- `omx_discord_bridge/.env.discord` values must never be printed
- only key existence checks are allowed
- if the env file becomes tracked, the secret guard must fail
