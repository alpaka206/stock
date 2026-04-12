from __future__ import annotations

import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / 'omx_discord_bridge' / '.env.discord'
REQUIRED_KEYS = (
    'DISCORD_GUILD_ID',
    'DISCORD_PARENT_CHANNEL_ID',
    'DISCORD_WEBHOOK_URL',
    'ALLOWED_DISCORD_USER_IDS',
    'DISCORD_BOT_TOKEN',
)
DISCORD_API_BASE = 'https://discord.com/api/v10'
CONVERSATION_LOG = ROOT / '.omx' / 'state' / 'TEAM_CONVERSATION.jsonl'
DISCORD_INBOX_LOG = ROOT / '.omx' / 'state' / 'DISCORD_INBOX.jsonl'
DISCORD_INBOX_SUMMARY = ROOT / '.omx' / 'state' / 'DISCORD_INBOX.md'
DISCORD_REPLY_STATE = ROOT / '.omx' / 'state' / 'DISCORD_REPLY_STATE.json'
BRIDGE_RUNTIME_STATUS = ROOT / '.omx' / 'runtime' / 'discord-bridge-status.json'
CONTROL_CHAR_RE = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')
RAW_UNICODE_ESCAPE_RE = re.compile(r'\\u[0-9a-fA-F]{4}')
DOUBLE_QUESTION_RE = re.compile(r'\?\?')
HANGUL_RE = re.compile(r'[가-힣]')


def ensure_state_dirs() -> None:
    (ROOT / '.omx' / 'state').mkdir(parents=True, exist_ok=True)
    (ROOT / '.omx' / 'runtime').mkdir(parents=True, exist_ok=True)


def sanitize_text(value: str) -> str:
    text = value.replace('\r\n', '\n').replace('\r', '\n')
    text = CONTROL_CHAR_RE.sub('', text).strip()
    question_count = text.count('?')
    if question_count >= 3 and not HANGUL_RE.search(text):
        ascii_letters = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        if ascii_letters < 8:
            return '[인코딩 손상으로 원문을 보존하지 못함]'
    text = DOUBLE_QUESTION_RE.sub('물음표 두 개', text)
    text = RAW_UNICODE_ESCAPE_RE.sub('[유니코드 이스케이프 제거]', text)
    return text


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): sanitize_value(item) for key, item in value.items()}
    return value


def write_runtime_status(*, status: str, detail: str = '', imported: int = 0, responded: int = 0) -> None:
    BRIDGE_RUNTIME_STATUS.write_text(
        json.dumps(
            {
                'status': status,
                'detail': detail,
                'imported': imported,
                'responded': responded,
                'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            },
            ensure_ascii=False,
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )


def load_env_values(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def load_env_keys(env_path: Path) -> dict[str, bool]:
    values = load_env_values(env_path)
    return {key: bool(values.get(key)) for key in REQUIRED_KEYS}


def parse_allowed_user_ids(raw: str) -> set[str]:
    return {item.strip() for item in raw.split(',') if item.strip()}


def build_webhook_url(webhook_url: str, thread_id: str | None) -> str:
    if not thread_id:
        return webhook_url
    parsed = urlparse(webhook_url)
    query = parse_qs(parsed.query)
    query['thread_id'] = [thread_id]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(sanitize_value(payload), ensure_ascii=False) + '\n')


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not path.exists():
        return items
    for raw in path.read_text(encoding='utf-8').splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            items.append(payload)
    return items


def rewrite_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for item in items:
            handle.write(json.dumps(sanitize_value(item), ensure_ascii=False) + '\n')


def repair_state_logs() -> None:
    for path in (DISCORD_INBOX_LOG, CONVERSATION_LOG):
        if not path.exists():
            continue
        rewrite_jsonl(path, [sanitize_value(item) for item in load_jsonl(path)])


def write_inbox_summary(imported: list[dict[str, Any]]) -> None:
    lines = ['# Discord Inbox', '']
    if not imported:
        lines.append('- 새로 들어온 Discord 메시지 없음')
    else:
        for item in imported[-20:]:
            author = item.get('author', 'unknown')
            content = item.get('content', '').strip() or '[빈 메시지]'
            lines.append(f'- {author}: {content}')
    DISCORD_INBOX_SUMMARY.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def load_reply_state() -> dict[str, str]:
    if not DISCORD_REPLY_STATE.exists():
        return {'last_message_id': ''}
    try:
        return json.loads(DISCORD_REPLY_STATE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {'last_message_id': ''}


def save_reply_state(last_message_id: str) -> None:
    DISCORD_REPLY_STATE.write_text(
        json.dumps({'last_message_id': last_message_id}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def send_discord_message(
    *,
    webhook_url: str,
    content: str,
    username: str,
    thread_id: str | None = None,
    source: str = 'agent',
    meeting_id: str = '',
    phase: str = '',
    trigger_id: str = '',
) -> dict[str, Any]:
    content = sanitize_text(content)
    username = sanitize_text(username)
    target_url = build_webhook_url(webhook_url, thread_id)
    payload = {
        'content': content,
        'username': username,
        'allowed_mentions': {'parse': []},
    }
    response = httpx.post(target_url, json=payload, timeout=15.0)
    response.raise_for_status()
    append_jsonl(
        CONVERSATION_LOG,
        {
            'source': source,
            'role': username,
            'content': content,
            'thread_id': thread_id or '',
            'meeting_id': meeting_id,
            'phase': phase,
            'trigger_id': trigger_id,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        },
    )
    write_runtime_status(status='event_sent', detail=f'{username} -> discord', responded=1)
    return {'ok': True, 'status_code': response.status_code}


def fetch_channel_messages(*, channel_id: str, bot_token: str, after: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
    params: dict[str, Any] = {'limit': min(max(limit, 1), 100)}
    if after:
        params['after'] = after
    response = httpx.get(
        f'{DISCORD_API_BASE}/channels/{channel_id}/messages',
        headers={'Authorization': f'Bot {bot_token}'},
        params=params,
        timeout=15.0,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        return []
    return list(reversed(payload))


def import_discord_replies(*, env_values: dict[str, str]) -> dict[str, Any]:
    channel_id = env_values.get('DISCORD_PARENT_CHANNEL_ID', '').strip()
    bot_token = env_values.get('DISCORD_BOT_TOKEN', '').strip()
    allowed_user_ids = parse_allowed_user_ids(env_values.get('ALLOWED_DISCORD_USER_IDS', ''))
    if not channel_id or not bot_token:
        return {'ok': False, 'imported': 0, 'detail': 'DISCORD_PARENT_CHANNEL_ID 또는 DISCORD_BOT_TOKEN 누락'}

    state = load_reply_state()
    messages = fetch_channel_messages(
        channel_id=channel_id,
        bot_token=bot_token,
        after=state.get('last_message_id') or None,
    )
    imported: list[dict[str, Any]] = []
    last_seen = state.get('last_message_id', '')
    for message in messages:
        author = message.get('author') or {}
        author_id = str(author.get('id', '')).strip()
        if allowed_user_ids and author_id not in allowed_user_ids:
            continue
        if author.get('bot'):
            continue
        payload = {
            'source': 'discord_user',
            'message_id': str(message.get('id', '')).strip(),
            'author_id': author_id,
            'author': sanitize_text(str(author.get('username', 'unknown'))),
            'content': sanitize_text(str(message.get('content', '')).strip()),
            'channel_id': channel_id,
            'thread_id': '',
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }
        if not payload['message_id'] or not payload['content']:
            continue
        append_jsonl(DISCORD_INBOX_LOG, payload)
        append_jsonl(CONVERSATION_LOG, payload)
        imported.append(payload)
        last_seen = payload['message_id'] or last_seen

    if last_seen:
        save_reply_state(last_seen)
    write_inbox_summary(imported)
    write_runtime_status(status='reply_sync_ok', detail='reply sync complete', imported=len(imported))
    return {'ok': True, 'imported': len(imported), 'detail': 'reply sync complete'}


def start_reply_poller(env_path: Path) -> threading.Thread:
    interval = int(os.getenv('DISCORD_POLL_INTERVAL_SECONDS', '10'))

    def loop() -> None:
        while True:
            try:
                env_values = load_env_values(env_path)
                if env_values:
                    import_discord_replies(env_values=env_values)
            except Exception as exc:
                write_runtime_status(status='poll_error', detail=str(exc))
            time.sleep(max(interval, 5))

    thread = threading.Thread(target=loop, daemon=True, name='discord-reply-poller')
    thread.start()
    return thread


class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != '/health':
            self.send_response(404)
            self.end_headers()
            return
        payload = {
            'ok': True,
            'bridge': 'discord-omx-bridge',
            'runtime': json.loads(BRIDGE_RUNTIME_STATUS.read_text(encoding='utf-8')) if BRIDGE_RUNTIME_STATUS.exists() else {},
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {'/event', '/sync-replies'}:
            self.send_response(404)
            self.end_headers()
            return

        bridge_env_file = Path(os.getenv('DISCORD_ENV_FILE', str(DEFAULT_ENV_FILE)))
        env_values = load_env_values(bridge_env_file)
        if self.path == '/sync-replies':
            try:
                result = import_discord_replies(env_values=env_values)
                self.send_response(200 if result.get('ok') else 503)
            except Exception as exc:
                result = {'ok': False, 'detail': str(exc)}
                write_runtime_status(status='sync_error', detail=str(exc))
                self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            return

        length = int(self.headers.get('Content-Length', '0'))
        raw_body = self.rfile.read(length).decode('utf-8') if length else '{}'
        payload = json.loads(raw_body or '{}')
        webhook_url = env_values.get('DISCORD_WEBHOOK_URL', '')
        if not webhook_url:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'detail': 'DISCORD_WEBHOOK_URL missing'}).encode('utf-8'))
            return

        content = str(payload.get('content', '')).strip()
        username = str(payload.get('username', 'executor')).strip() or 'executor'
        thread_id = str(payload.get('thread_id', '')).strip() or None
        meeting_id = str(payload.get('meeting_id', '')).strip()
        phase = str(payload.get('phase', '')).strip()
        trigger_id = str(payload.get('trigger_id', '')).strip()
        source = str(payload.get('source', 'agent')).strip() or 'agent'
        if not content:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'detail': 'content required'}).encode('utf-8'))
            return

        try:
            result = send_discord_message(
                webhook_url=webhook_url,
                content=content,
                username=username,
                thread_id=thread_id,
                source=source,
                meeting_id=meeting_id,
                phase=phase,
                trigger_id=trigger_id,
            )
        except Exception as exc:
            write_runtime_status(status='event_error', detail=str(exc))
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'detail': str(exc)}).encode('utf-8'))
            return

        self.send_response(202)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def main() -> int:
    ensure_state_dirs()
    repair_state_logs()
    env_path = Path(os.getenv('DISCORD_ENV_FILE', str(DEFAULT_ENV_FILE)))
    key_status = load_env_keys(env_path)
    host = os.getenv('DISCORD_BRIDGE_HOST', '127.0.0.1')
    port = int(os.getenv('DISCORD_BRIDGE_PORT', '8787'))
    write_runtime_status(status='starting', detail='bridge boot')
    print(json.dumps({'env_file_exists': env_path.exists(), 'keys': key_status}, ensure_ascii=False))
    if env_path.exists():
        start_reply_poller(env_path)
    server = HTTPServer((host, port), BridgeHandler)
    write_runtime_status(status='listening', detail=f'{host}:{port}')
    server.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
