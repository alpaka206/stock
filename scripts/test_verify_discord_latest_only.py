from __future__ import annotations

import json
import tempfile
from pathlib import Path

from verify_discord_latest_only import (
    DIAGNOSIS_ALREADY_HANDLED,
    DIAGNOSIS_DISALLOWED_HUMAN,
    DIAGNOSIS_NO_NEW_HUMAN,
    DIAGNOSIS_READY_FOR_LOOP,
    build_snapshot,
    classify_latest_only_blockage,
    determine_watch_status,
    verify_transition,
)


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


def live_message(message_id: str, *, author_id: str, username: str, bot: bool = False, content: str = "hello") -> dict:
    return {
        "id": message_id,
        "content": content,
        "timestamp": "2026-04-17T00:00:00.000000+00:00",
        "author": {
            "id": author_id,
            "username": username,
            "bot": bot,
        },
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


def test_diagnosis_marks_no_new_human_message() -> None:
    diagnosis = classify_latest_only_blockage(
        live_messages_after_cursor=[
            live_message("bot-1", author_id="bot", username="coordinator", bot=True),
            live_message("bot-2", author_id="bot", username="planner", bot=True),
        ],
        inbox_entries=[
            {"source": "discord_user", "message_id": "old-1", "author_id": "user-1", "author": "alice", "content": "old"}
        ],
        reply_last_message_id="old-1",
        handled_message_ids=["old-1"],
        allowed_user_ids={"user-1"},
    )
    if diagnosis["category"] != DIAGNOSIS_NO_NEW_HUMAN:
        raise AssertionError(f"expected no-new-human diagnosis, got {diagnosis}")


def test_diagnosis_marks_disallowed_human_message() -> None:
    diagnosis = classify_latest_only_blockage(
        live_messages_after_cursor=[
            live_message("bot-1", author_id="bot", username="coordinator", bot=True),
            live_message("human-1", author_id="user-2", username="bob", content="new human"),
        ],
        inbox_entries=[
            {"source": "discord_user", "message_id": "old-1", "author_id": "user-1", "author": "alice", "content": "old"}
        ],
        reply_last_message_id="old-1",
        handled_message_ids=["old-1"],
        allowed_user_ids={"user-1"},
    )
    if diagnosis["category"] != DIAGNOSIS_DISALLOWED_HUMAN:
        raise AssertionError(f"expected disallowed-human diagnosis, got {diagnosis}")


def test_diagnosis_marks_ready_for_loop_when_imported_but_not_handled() -> None:
    diagnosis = classify_latest_only_blockage(
        live_messages_after_cursor=[
            live_message("human-2", author_id="user-1", username="alice", content="new allowed"),
        ],
        inbox_entries=[
            {"source": "discord_user", "message_id": "old-1", "author_id": "user-1", "author": "alice", "content": "old"},
            {"source": "discord_user", "message_id": "human-2", "author_id": "user-1", "author": "alice", "content": "new allowed"},
        ],
        reply_last_message_id="human-2",
        handled_message_ids=["old-1"],
        allowed_user_ids={"user-1"},
    )
    if diagnosis["category"] != DIAGNOSIS_READY_FOR_LOOP:
        raise AssertionError(f"expected ready-for-loop diagnosis, got {diagnosis}")


def test_diagnosis_marks_already_handled_when_loop_consumed_latest_allowed() -> None:
    diagnosis = classify_latest_only_blockage(
        live_messages_after_cursor=[
            live_message("human-3", author_id="user-1", username="alice", content="latest allowed"),
        ],
        inbox_entries=[
            {"source": "discord_user", "message_id": "old-1", "author_id": "user-1", "author": "alice", "content": "old"},
            {"source": "discord_user", "message_id": "human-3", "author_id": "user-1", "author": "alice", "content": "latest allowed"},
        ],
        reply_last_message_id="human-3",
        handled_message_ids=["old-1", "human-3"],
        allowed_user_ids={"user-1"},
    )
    if diagnosis["category"] != DIAGNOSIS_ALREADY_HANDLED:
        raise AssertionError(f"expected already-handled diagnosis, got {diagnosis}")


def test_watch_status_waits_for_message_before_new_allowed_message() -> None:
    watch_status = determine_watch_status(
        baseline_message_id="old-1",
        diagnosis_payload={
            "diagnosis": {
                "category": DIAGNOSIS_NO_NEW_HUMAN,
                "comparison": {
                    "live_latest_allowed_after_cursor": None,
                },
            }
        },
        current_snapshot={
            "loop_state": {
                "handled_discord_message_ids": ["old-1"],
                "last_meeting_id": "meeting-before",
            }
        },
        before_snapshot_path=".omx/state/discord-latest-before.json",
    )
    if watch_status["status"] != "waiting_for_message":
        raise AssertionError(f"expected waiting_for_message status, got {watch_status}")
    if watch_status["ready_for_verify"] is not False:
        raise AssertionError(f"expected ready_for_verify false, got {watch_status}")


def test_watch_status_builds_verify_command_when_fixed_cursor_message_is_handled() -> None:
    watch_status = determine_watch_status(
        baseline_message_id="old-1",
        diagnosis_payload={
            "diagnosis": {
                "category": DIAGNOSIS_ALREADY_HANDLED,
                "comparison": {
                    "live_latest_allowed_after_cursor": {
                        "message_id": "new-4",
                        "author_id": "user-1",
                        "author": "alice",
                    },
                },
            }
        },
        current_snapshot={
            "loop_state": {
                "handled_discord_message_ids": ["old-1", "new-4"],
                "last_meeting_id": "meeting-4",
            }
        },
        before_snapshot_path=".omx/state/discord-latest-before.json",
    )
    if watch_status["status"] != "handled":
        raise AssertionError(f"expected handled status, got {watch_status}")
    if watch_status["ready_for_verify"] is not True:
        raise AssertionError(f"expected ready_for_verify true, got {watch_status}")
    expected = (
        "python scripts/verify_discord_latest_only.py verify "
        "--before .omx/state/discord-latest-before.json "
        "--message-id new-4 "
        "--meeting-id meeting-4"
    )
    if watch_status["verify_command"] != expected:
        raise AssertionError(f"unexpected verify_command: {watch_status}")


def main() -> int:
    test_snapshot_and_verify_pass()
    test_verify_fails_when_executor_metadata_missing()
    test_verify_fails_when_trigger_message_id_is_missing()
    test_diagnosis_marks_no_new_human_message()
    test_diagnosis_marks_disallowed_human_message()
    test_diagnosis_marks_ready_for_loop_when_imported_but_not_handled()
    test_diagnosis_marks_already_handled_when_loop_consumed_latest_allowed()
    test_watch_status_waits_for_message_before_new_allowed_message()
    test_watch_status_builds_verify_command_when_fixed_cursor_message_is_handled()
    print("discord latest-only verification helper tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
