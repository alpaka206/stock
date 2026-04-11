# Discord Status

- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `.env.discord`
- `.env.discord` exists: no
- `.env.discord` tracked: no
- required keys:
  - DISCORD_GUILD_ID
  - DISCORD_PARENT_CHANNEL_ID
  - DISCORD_WEBHOOK_URL
  - ALLOWED_DISCORD_USER_IDS
  - DISCORD_BOT_TOKEN
- bridge scaffold: installed
- runtime: blocked until `.env.discord` exists
- reply injection: blocked
