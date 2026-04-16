from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_DIR = ROOT / ".omx" / "state"
DEFAULT_ENV_FILE = ROOT / "omx_discord_bridge" / ".env.discord"
REQUIRED_ROLE_PHASES = ("planner", "critic", "researcher", "architect", "executor", "verifier")
REQUIRED_ROLE_METADATA_KEYS = (
    "status",
    "summary",
    "rationale",
    "proposed_action",
    "team_message",
    "reply_to",
    "risks",
    "verification",
    "changed_files",
    "followups",
    "confidence",
    "needs_human",
)
START_MESSAGE = "\uc791\uc5c5\uc744 \uc2dc\uc791\ud569\ub2c8\ub2e4."
DIAGNOSIS_NO_NEW_HUMAN = "no_new_human_message"
DIAGNOSIS_DISALLOWED_HUMAN = "disallowed_human_message"
DIAGNOSIS_IMPORT_STALLED = "import_cursor_stalled"
DIAGNOSIS_ALREADY_HANDLED = "already_handled"
DIAGNOSIS_READY_FOR_LOOP = "ready_for_loop"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from omx_discord_bridge.discord_omx_bridge import fetch_channel_messages, load_env_values, parse_allowed_user_ids


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    evidence: dict[str, Any]
    errors: list[str]
    warnings: list[str]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def latest_iso_from_entries(entries: list[dict[str, Any]]) -> str:
    values = [str(entry.get("created_at", "")).strip() for entry in entries if str(entry.get("created_at", "")).strip()]
    return values[-1] if values else ""


def latest_meeting_id(entries: list[dict[str, Any]]) -> str:
    values = [str(entry.get("meeting_id", "")).strip() for entry in entries if str(entry.get("meeting_id", "")).strip()]
    return values[-1] if values else ""


def build_snapshot(state_dir: Path) -> dict[str, Any]:
    inbox_entries = read_jsonl(state_dir / "DISCORD_INBOX.jsonl")
    user_entries = [entry for entry in inbox_entries if str(entry.get("source", "")).strip() == "discord_user"]
    latest_user = user_entries[-1] if user_entries else {}
    loop_state = read_json(state_dir / "OMX_LOOP_STATE.json", {})
    reply_state = read_json(state_dir / "DISCORD_REPLY_STATE.json", {})
    conversation_entries = read_jsonl(state_dir / "TEAM_CONVERSATION.jsonl")
    start_messages = [
        entry
        for entry in conversation_entries
        if str(entry.get("content", "")).strip() == START_MESSAGE
    ]

    return {
        "captured_at": latest_iso_from_entries(conversation_entries) or "",
        "state_dir": str(state_dir),
        "discord_inbox": {
            "discord_user_count": len(user_entries),
            "latest_message_id": str(latest_user.get("message_id", "")).strip(),
            "latest_author": str(latest_user.get("author", "")).strip(),
            "latest_created_at": str(latest_user.get("created_at", "")).strip(),
            "message_ids": [str(entry.get("message_id", "")).strip() for entry in user_entries if str(entry.get("message_id", "")).strip()],
        },
        "discord_reply_state": {
            "last_message_id": str(reply_state.get("last_message_id", "")).strip(),
        },
        "loop_state": {
            "iteration": loop_state.get("iteration"),
            "meeting_counter": loop_state.get("meeting_counter"),
            "last_meeting_id": str(loop_state.get("last_meeting_id", "")).strip(),
            "handled_discord_message_ids": [
                str(item).strip()
                for item in loop_state.get("handled_discord_message_ids", [])
                if str(item).strip()
            ],
            "pending_followup": loop_state.get("pending_followup", {}),
        },
        "team_conversation": {
            "entry_count": len(conversation_entries),
            "latest_meeting_id": latest_meeting_id(conversation_entries),
            "start_message_count": len(start_messages),
            "start_message_entries": [
                {
                    "meeting_id": str(entry.get("meeting_id", "")).strip(),
                    "role": str(entry.get("role", "")).strip(),
                    "created_at": str(entry.get("created_at", "")).strip(),
                }
                for entry in start_messages[-10:]
            ],
        },
    }


def compare_count(before: dict[str, Any], after: dict[str, Any], *keys: str) -> int | None:
    current_before: Any = before
    current_after: Any = after
    for key in keys:
        if not isinstance(current_before, dict) or not isinstance(current_after, dict):
            return None
        current_before = current_before.get(key)
        current_after = current_after.get(key)
    if isinstance(current_before, int) and isinstance(current_after, int):
        return current_after - current_before
    return None


def get_meeting_entries(state_dir: Path, meeting_id: str) -> list[dict[str, Any]]:
    return [
        entry
        for entry in read_jsonl(state_dir / "TEAM_CONVERSATION.jsonl")
        if str(entry.get("meeting_id", "")).strip() == meeting_id
    ]


def fetch_discord_messages_page(*, channel_id: str, bot_token: str, after: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    return fetch_channel_messages(channel_id=channel_id, bot_token=bot_token, after=after, limit=limit)


def collect_live_messages_after_cursor(
    *,
    channel_id: str,
    bot_token: str,
    after_message_id: str,
    max_pages: int,
    page_size: int,
) -> dict[str, Any]:
    cursor = after_message_id.strip() or None
    pages_scanned = 0
    messages: list[dict[str, Any]] = []
    truncated = False
    while pages_scanned < max_pages:
        batch = fetch_discord_messages_page(channel_id=channel_id, bot_token=bot_token, after=cursor, limit=page_size)
        pages_scanned += 1
        if not batch:
            break
        messages.extend(batch)
        next_cursor = str(batch[-1].get("id", "")).strip()
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        if len(batch) < min(max(page_size, 1), 100):
            break
    else:
        truncated = True

    return {
        "pages_scanned": pages_scanned,
        "message_count": len(messages),
        "truncated": truncated,
        "messages": messages,
    }


def summarize_live_message(message: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(message, dict):
        return None
    author = message.get("author") or {}
    return {
        "message_id": str(message.get("id", "")).strip(),
        "author_id": str(author.get("id", "")).strip(),
        "author": str(author.get("username", "")).strip(),
        "bot": bool(author.get("bot")),
        "content": str(message.get("content", "")).strip(),
        "timestamp": str(message.get("timestamp", "")).strip(),
    }


def classify_latest_only_blockage(
    *,
    live_messages_after_cursor: list[dict[str, Any]],
    inbox_entries: list[dict[str, Any]],
    reply_last_message_id: str,
    handled_message_ids: list[str],
    allowed_user_ids: set[str],
) -> dict[str, Any]:
    inbox_user_entries = [entry for entry in inbox_entries if str(entry.get("source", "")).strip() == "discord_user"]
    inbox_latest = inbox_user_entries[-1] if inbox_user_entries else {}
    inbox_ids = {
        str(entry.get("message_id", "")).strip()
        for entry in inbox_user_entries
        if str(entry.get("message_id", "")).strip()
    }
    handled_set = {str(item).strip() for item in handled_message_ids if str(item).strip()}

    human_messages = [
        message
        for message in live_messages_after_cursor
        if not bool((message.get("author") or {}).get("bot"))
    ]
    allowed_human_messages = [
        message
        for message in human_messages
        if not allowed_user_ids or str((message.get("author") or {}).get("id", "")).strip() in allowed_user_ids
    ]

    latest_human = human_messages[-1] if human_messages else None
    latest_allowed = allowed_human_messages[-1] if allowed_human_messages else None
    latest_allowed_id = str((latest_allowed or {}).get("id", "")).strip()
    handled_contains_latest_allowed = bool(latest_allowed_id and latest_allowed_id in handled_set)
    inbox_contains_latest_allowed = bool(latest_allowed_id and latest_allowed_id in inbox_ids)
    reply_matches_latest_allowed = bool(latest_allowed_id and reply_last_message_id == latest_allowed_id)

    if latest_human is None:
        category = DIAGNOSIS_NO_NEW_HUMAN
        reason = "reply_state.last_message_id 이후에 새 human 메시지가 없습니다."
    elif latest_allowed is None:
        category = DIAGNOSIS_DISALLOWED_HUMAN
        reason = "reply_state.last_message_id 이후 human 메시지는 있지만 allowed author가 아닙니다."
    elif not inbox_contains_latest_allowed or not reply_matches_latest_allowed:
        category = DIAGNOSIS_IMPORT_STALLED
        reason = "최신 allowed human 메시지가 live Discord에는 있지만 inbox 또는 reply_state에 아직 반영되지 않았습니다."
    elif handled_contains_latest_allowed:
        category = DIAGNOSIS_ALREADY_HANDLED
        reason = "최신 allowed human 메시지가 inbox/reply_state에 반영됐고 loop_state.handled에도 있어 새 trigger 후보가 아닙니다."
    else:
        category = DIAGNOSIS_READY_FOR_LOOP
        reason = "최신 allowed human 메시지가 inbox/reply_state에 반영됐고 loop_state.handled에는 없어 다음 loop trigger 후보입니다."

    return {
        "category": category,
        "ready_for_loop": category == DIAGNOSIS_READY_FOR_LOOP,
        "reason": reason,
        "comparison": {
            "live_latest_human_after_cursor": summarize_live_message(latest_human),
            "live_latest_allowed_after_cursor": summarize_live_message(latest_allowed),
            "inbox_latest_discord_user": {
                "message_id": str(inbox_latest.get("message_id", "")).strip(),
                "author_id": str(inbox_latest.get("author_id", "")).strip(),
                "author": str(inbox_latest.get("author", "")).strip(),
            },
            "reply_state_last_message_id": reply_last_message_id,
            "loop_handled_contains_latest_allowed": handled_contains_latest_allowed,
        },
        "counts": {
            "live_messages_after_cursor": len(live_messages_after_cursor),
            "human_messages_after_cursor": len(human_messages),
            "allowed_human_messages_after_cursor": len(allowed_human_messages),
            "inbox_discord_user_count": len(inbox_user_entries),
            "handled_discord_message_count": len(handled_set),
        },
    }


def diagnose_latest_only_state(
    *,
    state_dir: Path,
    env_file: Path,
    max_pages: int,
    page_size: int,
    live_after_message_id: str | None = None,
) -> dict[str, Any]:
    snapshot = build_snapshot(state_dir)
    env_values = load_env_values(env_file)
    channel_id = env_values.get("DISCORD_PARENT_CHANNEL_ID", "").strip()
    bot_token = env_values.get("DISCORD_BOT_TOKEN", "").strip()
    if not channel_id or not bot_token:
        raise SystemExit("DISCORD_PARENT_CHANNEL_ID 또는 DISCORD_BOT_TOKEN 이 없어 live diagnosis를 실행할 수 없습니다.")

    reply_last_message_id = str(snapshot.get("discord_reply_state", {}).get("last_message_id", "")).strip()
    effective_live_after_message_id = (
        str(live_after_message_id).strip()
        if live_after_message_id is not None
        else reply_last_message_id
    )
    live_result = collect_live_messages_after_cursor(
        channel_id=channel_id,
        bot_token=bot_token,
        after_message_id=effective_live_after_message_id,
        max_pages=max_pages,
        page_size=page_size,
    )
    diagnosis = classify_latest_only_blockage(
        live_messages_after_cursor=list(live_result.get("messages", [])),
        inbox_entries=read_jsonl(state_dir / "DISCORD_INBOX.jsonl"),
        reply_last_message_id=reply_last_message_id,
        handled_message_ids=list(snapshot.get("loop_state", {}).get("handled_discord_message_ids", [])),
        allowed_user_ids=parse_allowed_user_ids(env_values.get("ALLOWED_DISCORD_USER_IDS", "")),
    )
    return {
        "ok": True,
        "state_dir": str(state_dir),
        "env_file": str(env_file),
        "reply_last_message_id": reply_last_message_id,
        "live_after_message_id": effective_live_after_message_id,
        "live_scan": {
            "pages_scanned": int(live_result.get("pages_scanned", 0)),
            "message_count": int(live_result.get("message_count", 0)),
            "truncated": bool(live_result.get("truncated", False)),
        },
        "diagnosis": diagnosis,
    }


def latest_allowed_message_from_diagnosis(payload: dict[str, Any]) -> dict[str, Any] | None:
    diagnosis = payload.get("diagnosis", {})
    if not isinstance(diagnosis, dict):
        return None
    comparison = diagnosis.get("comparison", {})
    if not isinstance(comparison, dict):
        return None
    latest_allowed = comparison.get("live_latest_allowed_after_cursor")
    if not isinstance(latest_allowed, dict):
        return None
    message_id = str(latest_allowed.get("message_id", "")).strip()
    return latest_allowed if message_id else None


def build_verify_command(before_path: str, message_id: str, meeting_id: str) -> str:
    return (
        "python scripts/verify_discord_latest_only.py verify "
        f"--before {before_path} "
        f"--message-id {message_id} "
        f"--meeting-id {meeting_id}"
    )


def determine_watch_status(
    *,
    baseline_message_id: str,
    diagnosis_payload: dict[str, Any],
    current_snapshot: dict[str, Any],
    before_snapshot_path: str,
) -> dict[str, Any]:
    latest_allowed = latest_allowed_message_from_diagnosis(diagnosis_payload)
    latest_allowed_id = str((latest_allowed or {}).get("message_id", "")).strip()
    handled_ids = [
        str(item).strip()
        for item in current_snapshot.get("loop_state", {}).get("handled_discord_message_ids", [])
        if str(item).strip()
    ]
    latest_meeting_id = str(current_snapshot.get("loop_state", {}).get("last_meeting_id", "")).strip()

    status = "waiting_for_message"
    ready_for_verify = False
    verify_command = ""

    if latest_allowed_id and latest_allowed_id != baseline_message_id:
        if latest_allowed_id in handled_ids and latest_meeting_id:
            status = "handled"
            ready_for_verify = True
            verify_command = build_verify_command(before_snapshot_path, latest_allowed_id, latest_meeting_id)
        else:
            status = "waiting_for_loop"

    return {
        "status": status,
        "ready_for_verify": ready_for_verify,
        "latest_allowed_message": latest_allowed,
        "message_id": latest_allowed_id,
        "meeting_id": latest_meeting_id if ready_for_verify else "",
        "verify_command": verify_command,
    }


def watch_latest_only_state(
    *,
    state_dir: Path,
    env_file: Path,
    snapshot_output: Path,
    timeout_seconds: float,
    poll_interval_seconds: float,
    max_pages: int,
    page_size: int,
) -> dict[str, Any]:
    before_snapshot = build_snapshot(state_dir)
    write_json_file(snapshot_output, before_snapshot)
    baseline_message_id = str(before_snapshot.get("discord_reply_state", {}).get("last_message_id", "")).strip()
    deadline = time.monotonic() + max(timeout_seconds, 0.1)
    polls = 0
    last_payload: dict[str, Any] | None = None
    last_watch_status: dict[str, Any] | None = None

    while True:
        polls += 1
        current_snapshot = build_snapshot(state_dir)
        payload = diagnose_latest_only_state(
            state_dir=state_dir,
            env_file=env_file,
            max_pages=max_pages,
            page_size=page_size,
            live_after_message_id=baseline_message_id,
        )
        watch_status = determine_watch_status(
            baseline_message_id=baseline_message_id,
            diagnosis_payload=payload,
            current_snapshot=current_snapshot,
            before_snapshot_path=str(snapshot_output),
        )
        last_payload = payload
        last_watch_status = watch_status
        if watch_status.get("ready_for_verify") is True:
            return {
                "ok": True,
                "before_snapshot": before_snapshot,
                "before_snapshot_path": str(snapshot_output),
                "baseline_message_id": baseline_message_id,
                "polls": polls,
                "diagnosis": payload.get("diagnosis", {}),
                "watch_status": watch_status,
            }
        if time.monotonic() >= deadline:
            break
        time.sleep(max(poll_interval_seconds, 0.2))

    return {
        "ok": False,
        "before_snapshot": before_snapshot,
        "before_snapshot_path": str(snapshot_output),
        "baseline_message_id": baseline_message_id,
        "polls": polls,
        "diagnosis": (last_payload or {}).get("diagnosis", {}),
        "watch_status": last_watch_status or {
            "status": "waiting_for_message",
            "ready_for_verify": False,
            "latest_allowed_message": None,
            "message_id": "",
            "meeting_id": "",
            "verify_command": "",
        },
    }


def verify_transition(
    *,
    before_snapshot: dict[str, Any],
    state_dir: Path,
    message_id: str,
    meeting_id: str,
    superseded_message_ids: list[str],
    expect_start_message_delta: int,
    allow_preexisting_message: bool,
    required_phases: tuple[str, ...] = REQUIRED_ROLE_PHASES,
) -> VerificationResult:
    after_snapshot = build_snapshot(state_dir)
    errors: list[str] = []
    warnings: list[str] = []

    before_ids = set(before_snapshot.get("discord_inbox", {}).get("message_ids", []))
    after_ids = set(after_snapshot.get("discord_inbox", {}).get("message_ids", []))
    handled_ids = set(after_snapshot.get("loop_state", {}).get("handled_discord_message_ids", []))

    if not allow_preexisting_message and message_id in before_ids:
        errors.append(f"message_id already existed in the before snapshot: {message_id}")
    if message_id not in after_ids:
        errors.append(f"DISCORD_INBOX.jsonl is missing message_id: {message_id}")
    if after_snapshot.get("discord_inbox", {}).get("latest_message_id") != message_id:
        errors.append(
            "DISCORD_INBOX.jsonl latest_message_id mismatch: "
            f"{after_snapshot.get('discord_inbox', {}).get('latest_message_id')!r}"
        )
    if after_snapshot.get("discord_reply_state", {}).get("last_message_id") != message_id:
        errors.append(
            "DISCORD_REPLY_STATE.json last_message_id mismatch: "
            f"{after_snapshot.get('discord_reply_state', {}).get('last_message_id')!r}"
        )
    if message_id not in handled_ids:
        errors.append(f"OMX_LOOP_STATE.json handled_discord_message_ids is missing message_id: {message_id}")
    if after_snapshot.get("loop_state", {}).get("last_meeting_id") != meeting_id:
        errors.append(
            "OMX_LOOP_STATE.json last_meeting_id mismatch: "
            f"{after_snapshot.get('loop_state', {}).get('last_meeting_id')!r}"
        )

    meeting_delta = compare_count(before_snapshot, after_snapshot, "loop_state", "meeting_counter")
    if meeting_delta is not None and meeting_delta < 1:
        warnings.append(f"meeting_counter increased by less than 1: {meeting_delta}")

    for superseded_id in superseded_message_ids:
        if superseded_id not in handled_ids:
            errors.append(f"handled_discord_message_ids is missing superseded message_id: {superseded_id}")
        if superseded_id == message_id:
            errors.append("superseded message_id list contains the latest message_id")

    meeting_entries = get_meeting_entries(state_dir, meeting_id)
    phase_entries = {
        phase: next((entry for entry in meeting_entries if str(entry.get("phase", "")).strip() == phase), None)
        for phase in required_phases
    }
    phase_positions = [
        next(
            (index for index, entry in enumerate(meeting_entries) if str(entry.get("phase", "")).strip() == phase),
            None,
        )
        for phase in required_phases
    ]
    if any(position is None for position in phase_positions):
        missing = [phase for phase, position in zip(required_phases, phase_positions) if position is None]
        errors.append(f"TEAM_CONVERSATION.jsonl is missing required phases: {', '.join(missing)}")
    elif phase_positions != sorted(phase_positions):
        errors.append(f"TEAM_CONVERSATION.jsonl phase order mismatch: {list(zip(required_phases, phase_positions))}")

    for phase, entry in phase_entries.items():
        if entry is None:
            continue
        for key in REQUIRED_ROLE_METADATA_KEYS:
            if key not in entry:
                errors.append(f"phase={phase} is missing metadata key: {key}")
                continue
            value = entry.get(key)
            if key in {"reply_to", "risks", "verification", "changed_files", "followups"}:
                if not isinstance(value, list):
                    errors.append(f"phase={phase} metadata {key} is not a list")
            elif key in {"team_message", "summary", "rationale", "proposed_action", "status"}:
                if not str(value).strip():
                    errors.append(f"phase={phase} metadata {key} is empty")
        if not isinstance(entry.get("reply_to"), list) or not entry.get("reply_to"):
            errors.append(f"phase={phase} reply_to is empty")
        if not str(entry.get("team_message", "")).strip():
            errors.append(f"phase={phase} team_message is empty")
        if str(entry.get("trigger_kind", "")).strip() != "discord_user":
            errors.append(f"phase={phase} trigger_kind mismatch: {entry.get('trigger_kind')!r}")
        if str(entry.get("trigger_message_id", "")).strip() != message_id:
            errors.append(
                f"phase={phase} trigger_message_id mismatch: {entry.get('trigger_message_id')!r}"
            )
        phase_superseded = entry.get("superseded_message_ids", [])
        if not isinstance(phase_superseded, list):
            errors.append(f"phase={phase} superseded_message_ids is not a list")
        else:
            normalized_phase_superseded = [str(item).strip() for item in phase_superseded if str(item).strip()]
            if normalized_phase_superseded != superseded_message_ids:
                errors.append(
                    "phase="
                    f"{phase} superseded_message_ids mismatch: {normalized_phase_superseded!r}"
                )

    start_delta = compare_count(before_snapshot, after_snapshot, "team_conversation", "start_message_count")
    if start_delta is None:
        warnings.append("start_message_count comparison was skipped")
    elif start_delta != expect_start_message_delta:
        errors.append(
            "start message delta mismatch: "
            f"expected={expect_start_message_delta}, actual={start_delta}"
        )

    evidence = {
        "before": before_snapshot,
        "after": after_snapshot,
        "message_id": message_id,
        "meeting_id": meeting_id,
        "superseded_message_ids": superseded_message_ids,
        "meeting_phase_order": [str(entry.get("phase", "")).strip() for entry in meeting_entries],
        "meeting_entry_count": len(meeting_entries),
        "start_message_delta": start_delta,
    }
    return VerificationResult(ok=not errors, evidence=evidence, errors=errors, warnings=warnings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture and verify Discord latest-only evidence across OMX state files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Capture the current state snapshot.")
    snapshot.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="State directory. Default: .omx/state")
    snapshot.add_argument("--output", help="Optional JSON file path to write the snapshot to.")
    snapshot.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")

    verify = subparsers.add_parser("verify", help="Verify a before/after transition against a message_id and meeting_id.")
    verify.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="State directory. Default: .omx/state")
    verify.add_argument("--before", required=True, help="Path to a snapshot JSON captured before execution.")
    verify.add_argument("--message-id", required=True, help="Expected latest Discord user message id.")
    verify.add_argument("--meeting-id", required=True, help="Meeting id that should own the role outputs.")
    verify.add_argument(
        "--superseded-message-id",
        action="append",
        default=[],
        help="Optional superseded Discord message id that must be marked handled without becoming latest.",
    )
    verify.add_argument(
        "--expect-start-message-delta",
        type=int,
        default=0,
        help="Expected increase in the fixed start message count between the before snapshot and the current state.",
    )
    verify.add_argument(
        "--allow-preexisting-message",
        action="store_true",
        help="Allow the target message id to already exist in the before snapshot.",
    )
    verify.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")

    diagnose = subparsers.add_parser("diagnose", help="Compare live Discord messages with inbox/reply_state/loop_state and classify why latest-only is blocked.")
    diagnose.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="State directory. Default: .omx/state")
    diagnose.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Discord env file. Default: omx_discord_bridge/.env.discord")
    diagnose.add_argument("--max-pages", type=int, default=5, help="Maximum Discord API pages to scan after reply_state.last_message_id.")
    diagnose.add_argument("--page-size", type=int, default=100, help="Discord API page size per request. Max 100.")
    diagnose.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")

    watch = subparsers.add_parser(
        "watch",
        help="Capture a before snapshot, keep a fixed live cursor, and wait until the next allowed Discord user message is fully handled.",
    )
    watch.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="State directory. Default: .omx/state")
    watch.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Discord env file. Default: omx_discord_bridge/.env.discord")
    watch.add_argument(
        "--snapshot-output",
        default=str(DEFAULT_STATE_DIR / "discord-latest-before.json"),
        help="Path to write the before snapshot JSON. Default: .omx/state/discord-latest-before.json",
    )
    watch.add_argument("--timeout-seconds", type=float, default=180.0, help="How long to wait for the next allowed message to be handled.")
    watch.add_argument("--poll-interval-seconds", type=float, default=3.0, help="Polling interval while waiting for the next allowed message.")
    watch.add_argument("--max-pages", type=int, default=5, help="Maximum Discord API pages to scan from the fixed baseline cursor.")
    watch.add_argument("--page-size", type=int, default=100, help="Discord API page size per request. Max 100.")
    watch.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")

    return parser.parse_args()


def format_snapshot(snapshot: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Discord latest-only snapshot",
            f"- state_dir: {snapshot.get('state_dir', '')}",
            f"- latest_message_id: {snapshot.get('discord_inbox', {}).get('latest_message_id', '')}",
            f"- reply_state.last_message_id: {snapshot.get('discord_reply_state', {}).get('last_message_id', '')}",
            f"- loop.last_meeting_id: {snapshot.get('loop_state', {}).get('last_meeting_id', '')}",
            f"- loop.handled_count: {len(snapshot.get('loop_state', {}).get('handled_discord_message_ids', []))}",
            f"- team.start_message_count: {snapshot.get('team_conversation', {}).get('start_message_count', 0)}",
            f"- team.entry_count: {snapshot.get('team_conversation', {}).get('entry_count', 0)}",
        ]
    )


def format_verification(result: VerificationResult) -> str:
    status = "PASS" if result.ok else "FAIL"
    lines = [
        f"Discord latest-only verification: {status}",
        f"- message_id: {result.evidence.get('message_id', '')}",
        f"- meeting_id: {result.evidence.get('meeting_id', '')}",
        f"- start_message_delta: {result.evidence.get('start_message_delta')}",
        f"- meeting_phase_order: {', '.join(result.evidence.get('meeting_phase_order', []))}",
    ]
    if result.warnings:
        lines.append("- warnings:")
        lines.extend(f"  - {item}" for item in result.warnings)
    if result.errors:
        lines.append("- errors:")
        lines.extend(f"  - {item}" for item in result.errors)
    return "\n".join(lines)


def format_diagnosis(payload: dict[str, Any]) -> str:
    diagnosis = payload.get("diagnosis", {})
    comparison = diagnosis.get("comparison", {})
    live_human = comparison.get("live_latest_human_after_cursor") or {}
    live_allowed = comparison.get("live_latest_allowed_after_cursor") or {}
    live_scan = payload.get("live_scan", {})
    lines = [
        "Discord latest-only diagnosis",
        f"- category: {diagnosis.get('category', '')}",
        f"- ready_for_loop: {diagnosis.get('ready_for_loop')}",
        f"- reason: {diagnosis.get('reason', '')}",
        f"- live_scan.pages_scanned: {live_scan.get('pages_scanned', 0)}",
        f"- live_scan.message_count: {live_scan.get('message_count', 0)}",
        f"- live_latest_human_after_cursor: {live_human.get('message_id', '')} / {live_human.get('author', '')} / {live_human.get('author_id', '')}",
        f"- live_latest_allowed_after_cursor: {live_allowed.get('message_id', '')} / {live_allowed.get('author', '')} / {live_allowed.get('author_id', '')}",
        f"- inbox_latest_discord_user: {comparison.get('inbox_latest_discord_user', {}).get('message_id', '')}",
        f"- reply_state.last_message_id: {comparison.get('reply_state_last_message_id', '')}",
        f"- loop_handled_contains_latest_allowed: {comparison.get('loop_handled_contains_latest_allowed')}",
    ]
    return "\n".join(lines)


def format_watch(payload: dict[str, Any]) -> str:
    watch_status = payload.get("watch_status", {})
    diagnosis = payload.get("diagnosis", {})
    latest_allowed = watch_status.get("latest_allowed_message") or {}
    lines = [
        "Discord latest-only watch",
        f"- ok: {payload.get('ok')}",
        f"- before_snapshot_path: {payload.get('before_snapshot_path', '')}",
        f"- baseline_message_id: {payload.get('baseline_message_id', '')}",
        f"- polls: {payload.get('polls', 0)}",
        f"- status: {watch_status.get('status', '')}",
        f"- diagnosis_category: {diagnosis.get('category', '')}",
        f"- latest_allowed_message: {watch_status.get('message_id', '')} / {latest_allowed.get('author', '')} / {latest_allowed.get('author_id', '')}",
        f"- meeting_id: {watch_status.get('meeting_id', '')}",
    ]
    verify_command = str(watch_status.get("verify_command", "")).strip()
    if verify_command:
        lines.append(f"- verify_command: {verify_command}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir)

    if args.command == "snapshot":
        snapshot = build_snapshot(state_dir)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        else:
            print(format_snapshot(snapshot))
        return 0

    if args.command == "diagnose":
        payload = diagnose_latest_only_state(
            state_dir=state_dir,
            env_file=Path(args.env_file),
            max_pages=max(int(args.max_pages), 1),
            page_size=max(int(args.page_size), 1),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(format_diagnosis(payload))
        return 0

    if args.command == "watch":
        payload = watch_latest_only_state(
            state_dir=state_dir,
            env_file=Path(args.env_file),
            snapshot_output=Path(args.snapshot_output),
            timeout_seconds=float(args.timeout_seconds),
            poll_interval_seconds=float(args.poll_interval_seconds),
            max_pages=max(int(args.max_pages), 1),
            page_size=max(int(args.page_size), 1),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(format_watch(payload))
        return 0 if bool(payload.get("ok")) else 1

    before_snapshot = read_json(Path(args.before), {})
    if not isinstance(before_snapshot, dict):
        raise SystemExit("before snapshot must be a JSON object")
    result = verify_transition(
        before_snapshot=before_snapshot,
        state_dir=state_dir,
        message_id=args.message_id,
        meeting_id=args.meeting_id,
        superseded_message_ids=[str(item).strip() for item in args.superseded_message_id if str(item).strip()],
        expect_start_message_delta=args.expect_start_message_delta,
        allow_preexisting_message=args.allow_preexisting_message,
    )
    payload = {
        "ok": result.ok,
        "errors": result.errors,
        "warnings": result.warnings,
        "evidence": result.evidence,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_verification(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
