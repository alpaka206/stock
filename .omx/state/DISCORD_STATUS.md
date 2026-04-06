# Discord Status

- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- `.env.discord` exists: yes
- `.env.discord` tracked: no
- bridge scaffold: installed
- live webhook forwarder: implemented
- reply polling: implemented
- shared logs:
  - `.omx/state/TEAM_CONVERSATION.jsonl`
  - `.omx/state/DISCORD_INBOX.jsonl`
  - `.omx/state/DISCORD_INBOX.md`
- quick test path: `scripts/test-discord-bridge.sh`
- manual reply sync: `scripts/sync-discord-replies.sh`
- reply injection: not implemented yet
