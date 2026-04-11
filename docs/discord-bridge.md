# Discord Bridge

## Current Status
- repo-local Discord bridge scaffold added
- real runtime requires `.env.discord`
- secret values are never printed or committed

## Decisions
- `.env.discord` is the single secret source
- `.env.discord` is read-only and must stay untracked
- bridge runtime is separated under `omx_discord_bridge/`

## Files
- `omx_discord_bridge/discord_omx_bridge.py`
- `omx_discord_bridge/requirements.txt`
- `omx_discord_bridge/.env.example`
- `scripts/run-discord-bridge.sh`
- `scripts/check-discord-bridge.sh`

## Run
```powershell
& 'C:\Program Files\Gitinash.exe' scripts/check-discord-bridge.sh
& 'C:\Program Files\Gitinash.exe' scripts/run-discord-bridge.sh
```

## Security
- `.env.discord` values must never be printed
- only key existence checks are allowed
- if `.env.discord` becomes tracked, the secret guard must fail

## Remaining Risks
- no real Discord env file in repo root yet
- thread-per-session / worker watcher is scaffold-only right now
- reply injection remains blocked until env and runtime are configured

## Next Work
- add actual `.env.discord` locally outside git
- run bridge health check
- connect OMX worker/session events to Discord threads
