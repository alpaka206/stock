from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_DIR = ROOT / ".omx" / "state"
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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
