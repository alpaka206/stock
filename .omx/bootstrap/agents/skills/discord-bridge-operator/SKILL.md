# discord-bridge-operator

name: discord-bridge-operator
description: manage Discord bridge scaffolding, status checks, and read-only `.env.discord` key presence checks.

## Trigger
- only when `ENABLE_DISCORD_BRIDGE=true`
- when Discord bridge scaffold, docs, or status files must be updated
- when `.env.discord` existence and key presence must be checked safely

## Do Not Trigger
- when actual secret values would need to be printed or committed
- when `.env.discord` does not exist and the task is not about bridge scaffolding or docs

## Rules
- treat `DISCORD_ENV_FILE` as read-only secret input
- never print the full file or any secret value
- check key presence only and write results to `DISCORD_STATUS.md`
- keep bridge scripts repo-local and non-interactive
- do not stage or commit `.env.discord`
