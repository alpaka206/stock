from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PREFIXES = (
    ".venv/",
    "node_modules/",
    "apps/web/.next/",
    ".pnpm-store/",
    ".omx/logs/",
    ".omx/runtime/",
    "dist/",
    "coverage/",
)
BANNED_FILE_PATTERNS = (
    ".env",
    ".env.*",
    ".env.discord",
    ".env.discord.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.crt",
    "*.cer",
    "*.der",
    "*.jks",
    "*.kdb",
    "*.secrets.*",
)
HIGH_RISK_PATTERN = re.compile(
    r"BEGIN (?:RSA|EC|OPENSSH|PRIVATE KEY)"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|AIza[0-9A-Za-z_-]{20,}"
    r"|hooks\.slack\.com/services/[A-Za-z0-9/_-]+"
    r"|discord\.com/api/webhooks/[A-Za-z0-9/_-]+"
    r"|x-goog-api-key\s*[:=]\s*[A-Za-z0-9_-]{12,}"
)
ALLOWED_TEMPLATE_BASENAMES = {
    ".env.example",
    ".env.discord.example",
}
CONTENT_SCAN_EXCLUDED = {
    "scripts/no_secrets_guard.py",
    "scripts/no_secrets_guard.sh",
}


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_git(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def is_excluded(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def iter_repo_files() -> list[str]:
    tracked = run_git("ls-files")
    staged = run_git("diff", "--cached", "--name-only")
    return sorted({path for path in [*tracked, *staged] if path and not is_excluded(path)})


def matches_banned_pattern(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = PurePosixPath(normalized).name
    if name in ALLOWED_TEMPLATE_BASENAMES:
        return False
    return any(
        fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(normalized, pattern)
        for pattern in BANNED_FILE_PATTERNS
    )


def scan_file(path: str) -> str | None:
    if path in CONTENT_SCAN_EXCLUDED:
        return None
    file_path = ROOT / path
    if not file_path.is_file():
        return None
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    match = HIGH_RISK_PATTERN.search(text)
    if not match:
        return None
    return str(text[: match.start()].count("\n") + 1)


def main() -> int:
    failed = False
    files = iter_repo_files()

    print("[guard] checking tracked and staged file names")
    for path in files:
        if matches_banned_pattern(path):
            print(f"[guard] banned filename match: {path}")
            failed = True

    print("[guard] scanning tracked and staged repo files for risky markers")
    for path in files:
        line_hint = scan_file(path)
        if line_hint is None:
            continue
        print(f"[guard] risky content hint: {path}:{line_hint}")
        failed = True

    if failed:
        print("[guard] failed")
        return 1

    print("[guard] passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
