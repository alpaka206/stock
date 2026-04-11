# Security Status

- `.env.discord` and `.env.discord.*` are ignored and guarded
- `.env.discord` tracked state: no
- `.env.discord` values must never be printed
- `scripts/no_secrets_guard.sh` fails if a Discord env file becomes tracked or staged
