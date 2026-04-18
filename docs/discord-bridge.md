# Discord Bridge

## Current Status
- bridge is now an ingest and relay layer, not a canned auto-replier
- real runtime reads `omx_discord_bridge/.env.discord` by default
- secret values are never printed or committed
- optional `OMX_DISCORD_MODE=signal-only` keeps detailed agent-to-agent chatter local while still posting user-facing signals
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
- `scripts/send-discord-event.py`
- `scripts/test-discord-bridge.sh`
- `scripts/test_discord_bridge.py`
- `scripts/no_secrets_guard.py`
- `scripts/verify_minimal.py`
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
6. Each role emits a Korean `team_message` that responds to the previous speaker instead of a flat smoke log.
7. Discord shows the role through the webhook username, so the visible body should avoid duplicated `meeting_id` or role prefixes while local logs keep the correlation fields.
8. Every role message and the closing summary are posted back to Discord and also logged locally when bridge fallback is used.
9. After `executor`, the loop runs `python scripts/no_secrets_guard.py` and `python scripts/verify_minimal.py`.

## Suggested Launch
```powershell
python omx_discord_bridge/discord_omx_bridge.py
$env:INFINITE_MODE='true'
python scripts/omx_autonomous_loop.py
```

Windows helpers:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-discord-bridge.ps1
powershell -ExecutionPolicy Bypass -File scripts/omx-loop.ps1 -InfiniteMode
```

## Discord Noise Control
- `OMX_DISCORD_MODE=all`: keep the current behavior and post every meeting step to Discord
- `OMX_DISCORD_MODE=signal-only`: post watcher ack, meeting start/end, repeated failure, and GitHub milestones only
- `OMX_DISCORD_MODE=local-only`: keep logs in `.omx/state/TEAM_CONVERSATION.jsonl` and skip Discord outbound messages
- imported user messages always stay in `.omx/state/DISCORD_INBOX.jsonl` and `.omx/state/TEAM_CONVERSATION.jsonl`

## Fast Bridge Smoke Test
```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/check-discord-bridge.sh
python scripts/test_discord_bridge.py
python scripts/send-discord-event.py --username coordinator --meeting-id manual-check --phase handoff --trigger-id manual-check "UTF-8 수동 알림 점검"
pnpm verify:automation
```

Expected result:
- `/health` returns JSON with runtime bridge status
- a short Korean dialogue between roles reaches Discord without `[meeting:...] role:` prefixes in the visible body
- `/sync-replies` returns JSON

## Read Path
- if you type in the configured Discord channel and your user ID is in `ALLOWED_DISCORD_USER_IDS`, the bridge imports the message into `.omx/state/DISCORD_INBOX.jsonl`
- imported messages are also appended to `.omx/state/TEAM_CONVERSATION.jsonl`
- the loop reads those files, holds an actual repo-aware meeting, and posts the discussion back to Discord in Korean
- autonomous internal meetings are also written to Discord and the local journal

## Security
- `omx_discord_bridge/.env.discord` values must never be printed

## Ralph Control
- `/ralph status`: current runtime, branch, and PR summary
- `/ralph pause`: next loop iteration pauses
- `/ralph resume`: clears pause and resumes
- `/ralph stop`: next loop iteration stops and `scripts/omx-loop.ps1` exits
- `/ralph nudge <message>`: injects a new follow-up action
- `/ralph goal <message>`: overrides the current goal
- `/ralph done <message>`: appends an extra done condition
- `/ralph logs`: returns the latest `.ralph/progress.md` summary
- `/ralph pr`: returns the current PR link when available
- only key existence checks are allowed
- if the env file becomes tracked, the secret guard must fail
