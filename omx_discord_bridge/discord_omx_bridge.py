from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / '.env.discord'
REQUIRED_KEYS = (
    'DISCORD_GUILD_ID',
    'DISCORD_PARENT_CHANNEL_ID',
    'DISCORD_WEBHOOK_URL',
    'ALLOWED_DISCORD_USER_IDS',
    'DISCORD_BOT_TOKEN',
)


def load_env_keys(env_path: Path) -> dict[str, bool]:
    found = {key: False for key in REQUIRED_KEYS}
    if not env_path.exists():
        return found
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _ = line.split('=', 1)
        key = key.strip()
        if key in found:
            found[key] = True
    return found


class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != '/health':
            self.send_response(404)
            self.end_headers()
            return
        payload = {
            'ok': True,
            'bridge': 'discord-omx-bridge',
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_POST(self) -> None:  # noqa: N802
        if self.path != '/event':
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(202)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'accepted': True}).encode('utf-8'))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def main() -> int:
    env_path = Path(os.getenv('DISCORD_ENV_FILE', str(DEFAULT_ENV_FILE)))
    key_status = load_env_keys(env_path)
    host = os.getenv('DISCORD_BRIDGE_HOST', '127.0.0.1')
    port = int(os.getenv('DISCORD_BRIDGE_PORT', '8787'))
    print(json.dumps({'env_file_exists': env_path.exists(), 'keys': key_status}, ensure_ascii=False))
    server = HTTPServer((host, port), BridgeHandler)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
