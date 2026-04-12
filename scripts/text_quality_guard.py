from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {
    '.git',
    'node_modules',
    '.venv',
    '.next',
    '.pnpm-store',
    'dist',
    'coverage',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
}
SKIP_NAMES = {'pnpm-lock.yaml', 'package-lock.json', 'yarn.lock', 'bun.lockb'}
TARGET_EXTS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.sh', '.ps1', '.toml', '.yaml', '.yml', '.json'}
DOC_PLACEHOLDER_EXTS = {'.md', '.txt'}
RAW_UNICODE_EXTS = {'.md', '.txt', '.toml', '.yaml', '.yml', '.json'}
MAX_SCAN_BYTES = 1_000_000
PLACEHOLDER_RE = re.compile(r'\?{3,}')
DOC_DOUBLE_QUESTION_RE = re.compile(r'(?<!\?)\?\?(?!\?)')
UNICODE_ESCAPE_RE = re.compile(r'\\u[0-9a-fA-F]{4}')
MOJIBAKE_RE = re.compile(r'(?:[\xC2\xC3\xE2][\x80-\xBF]){2,}')
REPLACEMENT_CHAR = chr(0xFFFD)
CORE_OMX_STATE_FILES = {
    'TASK.md',
    'STATE.md',
    'BACKLOG.md',
    'NEXT_PROMPT.md',
    'DISCORD_STATUS.md',
    'VERIFY_LAST_FAILURE.md',
}


def should_scan(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if path.name in SKIP_NAMES:
        return False
    if path.suffix.lower() not in TARGET_EXTS and path.name not in {'.gitignore', '.dockerignore'}:
        return False
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            return False
    except OSError:
        return False
    if parts and parts[0] == '.omx':
        if len(parts) >= 2 and parts[1] == 'state':
            return path.name in CORE_OMX_STATE_FILES
        if len(parts) >= 2 and parts[1] == 'bootstrap':
            return True
        return False
    return True


def iter_candidate_paths() -> list[Path]:
    items: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        current = Path(dirpath)
        rel = current.relative_to(ROOT)
        parts = rel.parts
        if not parts:
            dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]
        elif parts[0] == '.omx':
            if len(parts) == 1:
                dirnames[:] = [name for name in dirnames if name in {'state', 'bootstrap'}]
            elif len(parts) >= 2 and parts[1] == 'state':
                dirnames[:] = []
            elif len(parts) >= 2 and parts[1] == 'bootstrap':
                dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]
            else:
                dirnames[:] = []
        else:
            dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]

        for filename in filenames:
            path = current / filename
            if path.is_symlink() or not path.is_file():
                continue
            if should_scan(path):
                items.append(path)
    return items


def main() -> int:
    failures: list[str] = []
    for path in iter_candidate_paths():
        rel = str(path.relative_to(ROOT))
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            failures.append(f'{rel}: utf-8 decode failed')
            continue
        except OSError:
            failures.append(f'{rel}: read failed')
            continue

        if PLACEHOLDER_RE.search(text):
            failures.append(f'{rel}: placeholder sequence detected')
        if path.suffix.lower() in DOC_PLACEHOLDER_EXTS and DOC_DOUBLE_QUESTION_RE.search(text):
            failures.append(f'{rel}: document placeholder detected')
        if path.suffix.lower() in RAW_UNICODE_EXTS and UNICODE_ESCAPE_RE.search(text):
            failures.append(f'{rel}: raw unicode escape detected')
        if MOJIBAKE_RE.search(text):
            failures.append(f'{rel}: mojibake pattern detected')
        if REPLACEMENT_CHAR in text:
            failures.append(f'{rel}: replacement character detected')

        first_nonempty = next((line for line in text.splitlines() if line.strip()), '')
        if first_nonempty.startswith(' ') and '#!/usr/bin/env' in first_nonempty:
            failures.append(f'{rel}: shebang indentation detected')

    if failures:
        print('text quality guard failed:')
        for item in failures:
            print(f'- {item}')
        return 1

    print('text quality guard passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
