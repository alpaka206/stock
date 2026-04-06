# Discord Bridge

## Current Status
- repo-local Discord bridge scaffold added
- real runtime reads `omx_discord_bridge/.env.discord` by default
- secret values are never printed or committed
- bridge forwards `/event` payloads to the Discord webhook when the env file exists
- bridge polls Discord replies from the configured parent channel and stores them in repo-local logs

## Files
- `omx_discord_bridge/discord_omx_bridge.py`
- `omx_discord_bridge/requirements.txt`
- `omx_discord_bridge/.env.example`
- `scripts/run-discord-bridge.sh`
- `scripts/check-discord-bridge.sh`
- `scripts/test-discord-bridge.sh`
- `scripts/sync-discord-replies.sh`

## Shared Logs
- `.omx/state/TEAM_CONVERSATION.jsonl`
- `.omx/state/DISCORD_INBOX.jsonl`
- `.omx/state/DISCORD_INBOX.md`
- `.omx/state/DISCORD_REPLY_STATE.json`

## Fast 1-shot test
```powershell
& 'C:\Program Files\Gitinash.exe' scripts/check-discord-bridge.sh
& 'C:\Program Files\Gitinash.exe' scripts/test-discord-bridge.sh
```

Expected result:
- one `planner` message in Discord
- one `critic` message in Discord
- one `architect` message in Discord
- one `executor` message in Discord
- reply sync call returns JSON

## Read Path
- if you type in the configured Discord channel and your user ID is in `ALLOWED_DISCORD_USER_IDS`, the bridge will import the message into `.omx/state/DISCORD_INBOX.jsonl`
- imported messages are also appended to `.omx/state/TEAM_CONVERSATION.jsonl`
- agents can read those files as the shared cross-agent / cross-Discord conversation layer

## Security
- `omx_discord_bridge/.env.discord` values must never be printed
- only key existence checks are allowed
- if the env file becomes tracked, the secret guard must fail
