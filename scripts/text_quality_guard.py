from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git', 'node_modules', '.venv', '.next', '.pnpm-store', 'dist', 'coverage'}
TARGET_EXTS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.sh', '.ps1', '.toml', '.yaml', '.yml', '.json'}
PLACEHOLDER_RE = re.compile(r'\?{3,}')
UNICODE_ESCAPE_RE = re.compile(r'\\u[0-9a-fA-F]{4}')


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if any(part in EXCLUDE for part in path.parts):
            continue
        if path.suffix.lower() not in TARGET_EXTS and path.name not in {'.gitignore', '.dockerignore'}:
            continue
        text = path.read_text(encoding='utf-8')
        rel = str(path.relative_to(ROOT))
        if PLACEHOLDER_RE.search(text):
            failures.append(f'{rel}: placeholder sequence detected')
        if UNICODE_ESCAPE_RE.search(text):
            failures.append(f'{rel}: raw unicode escape detected')
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
