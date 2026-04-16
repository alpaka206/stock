from __future__ import annotations

import json
import tempfile
from pathlib import Path

from verify_discord_latest_only import build_snapshot, verify_transition


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, items: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def role_entry(
    meeting_id: str,
    phase: str,
    *,
    message_id: str,
    superseded_message_ids: list[str] | None = None,
) -> dict:
    return {
        "source": "agent",
        "role": phase,
        "phase": phase,
        "meeting_id": meeting_id,
        "trigger_id": f"discord-latest-{meeting_id}",
        "trigger_kind": "discord_user",
        "trigger_message_id": message_id,
        "superseded_message_ids": list(superseded_message_ids or []),
        "content": f"{phase} content",
        "summary": f"{phase} summary",
        "rationale": f"{phase} rationale",
        "proposed_action": f"{phase} action",
        "team_message": f"{phase} team message",
        "question_for_next": "",
        "reply_to": ["planner"] if phase != "planner" else ["user"],
        "risks": [],
        "verification": [],
        "changed_files": [],
        "followups": [],
        "confidence": 0.9,
        "needs_human": False,
        "status": "done",
        "created_at": "2026-04-17T00:00:00Z",
    }


def test_snapshot_and_verify_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="latest-only-pass-") as temp_dir:
        state_dir = Path(temp_dir)
        before_inbox = [
            {
                "source": "discord_user",
                "message_id": "old-1",
                "author": "alice",
                "content": "old message",
                "created_at": "2026-04-16T00:00:00Z",
            }
        ]
        write_jsonl(state_dir / "DISCORD_INBOX.jsonl", before_inbox)
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "old-1"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {
                "iteration": 7,
                "meeting_counter": 3,
                "last_meeting_id": "prev-meeting",
                "handled_discord_message_ids": ["old-1"],
            },
        )
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", [])

        before_snapshot = build_snapshot(state_dir)

        after_inbox = before_inbox + [
            {
                "source": "discord_user",
                "message_id": "new-1",
                "author": "alice",
                "content": "latest message",
                "created_at": "2026-04-17T00:00:00Z",
            }
        ]
        write_jsonl(state_dir / "DISCORD_INBOX.jsonl", after_inbox)
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "new-1"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {
                "iteration": 8,
                "meeting_counter": 4,
                "last_meeting_id": "meeting-1",
                "handled_discord_message_ids": ["old-1", "sup-1", "new-1"],
            },
        )
        meeting_entries = [
            role_entry("meeting-1", phase, message_id="new-1", superseded_message_ids=["sup-1"])
            for phase in ("planner", "critic", "researcher", "architect", "executor", "verifier")
        ]
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", meeting_entries)

        result = verify_transition(
            before_snapshot=before_snapshot,
            state_dir=state_dir,
            message_id="new-1",
            meeting_id="meeting-1",
            superseded_message_ids=["sup-1"],
            expect_start_message_delta=0,
            allow_preexisting_message=False,
        )
        if not result.ok:
            raise AssertionError(f"expected pass, got errors: {result.errors}")


def test_verify_fails_when_executor_metadata_missing() -> None:
    with tempfile.TemporaryDirectory(prefix="latest-only-fail-") as temp_dir:
        state_dir = Path(temp_dir)
        write_jsonl(state_dir / "DISCORD_INBOX.jsonl", [{"source": "discord_user", "message_id": "old-1", "content": "old"}])
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "old-1"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {"meeting_counter": 1, "last_meeting_id": "before", "handled_discord_message_ids": ["old-1"]},
        )
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", [])
        before_snapshot = build_snapshot(state_dir)

        write_jsonl(
            state_dir / "DISCORD_INBOX.jsonl",
            [
                {"source": "discord_user", "message_id": "old-1", "content": "old"},
                {"source": "discord_user", "message_id": "new-2", "content": "new"},
            ],
        )
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "new-2"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {"meeting_counter": 2, "last_meeting_id": "meeting-2", "handled_discord_message_ids": ["old-1", "new-2"]},
        )
        entries = [
            role_entry("meeting-2", phase, message_id="new-2")
            for phase in ("planner", "critic", "researcher", "architect", "executor", "verifier")
        ]
        del entries[4]["team_message"]
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", entries)

        result = verify_transition(
            before_snapshot=before_snapshot,
            state_dir=state_dir,
            message_id="new-2",
            meeting_id="meeting-2",
            superseded_message_ids=[],
            expect_start_message_delta=0,
            allow_preexisting_message=False,
        )
        if result.ok:
            raise AssertionError("expected verify_transition to fail when executor team_message is missing")
        if not any("team_message" in error for error in result.errors):
            raise AssertionError(f"missing team_message error not found: {result.errors}")


def test_verify_fails_when_trigger_message_id_is_missing() -> None:
    with tempfile.TemporaryDirectory(prefix="latest-only-trigger-metadata-") as temp_dir:
        state_dir = Path(temp_dir)
        write_jsonl(state_dir / "DISCORD_INBOX.jsonl", [{"source": "discord_user", "message_id": "old-1", "content": "old"}])
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "old-1"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {"meeting_counter": 5, "last_meeting_id": "before", "handled_discord_message_ids": ["old-1"]},
        )
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", [])
        before_snapshot = build_snapshot(state_dir)

        write_jsonl(
            state_dir / "DISCORD_INBOX.jsonl",
            [
                {"source": "discord_user", "message_id": "old-1", "content": "old"},
                {"source": "discord_user", "message_id": "new-3", "content": "new"},
            ],
        )
        write_json(state_dir / "DISCORD_REPLY_STATE.json", {"last_message_id": "new-3"})
        write_json(
            state_dir / "OMX_LOOP_STATE.json",
            {"meeting_counter": 6, "last_meeting_id": "meeting-3", "handled_discord_message_ids": ["old-1", "new-3"]},
        )
        entries = [
            role_entry("meeting-3", phase, message_id="new-3")
            for phase in ("planner", "critic", "researcher", "architect", "executor", "verifier")
        ]
        del entries[0]["trigger_message_id"]
        write_jsonl(state_dir / "TEAM_CONVERSATION.jsonl", entries)

        result = verify_transition(
            before_snapshot=before_snapshot,
            state_dir=state_dir,
            message_id="new-3",
            meeting_id="meeting-3",
            superseded_message_ids=[],
            expect_start_message_delta=0,
            allow_preexisting_message=False,
        )
        if result.ok:
            raise AssertionError("expected verify_transition to fail when trigger_message_id is missing")
        if not any("trigger_message_id" in error for error in result.errors):
            raise AssertionError(f"missing trigger_message_id error not found: {result.errors}")


def main() -> int:
    test_snapshot_and_verify_pass()
    test_verify_fails_when_executor_metadata_missing()
    test_verify_fails_when_trigger_message_id_is_missing()
    print("discord latest-only verification helper tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
