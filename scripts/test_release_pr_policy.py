from __future__ import annotations

from dataclasses import replace
from typing import Any

import omx_autonomous_loop as loop


def run_manual_release_creation_smoke(release_contract: loop.AgentsContract) -> None:
    loop_state: dict[str, Any] = {"github_flow": {"pr_number": 11, "issue_number": 7}}
    gh_calls: list[tuple[Any, ...]] = []
    status_messages: list[str] = []

    original_get_flow = loop.get_github_flow
    original_gh_json = loop.gh_json
    original_gh_command = loop.gh_command
    original_git_command = loop.git_command
    original_write_status = loop.write_github_automation_status

    def fake_get_github_flow(state: dict[str, Any]) -> dict[str, Any]:
        return state.setdefault("github_flow", {})

    def fake_gh_json(*args: Any, **kwargs: Any) -> Any:
        if args[:2] == ("pr", "view"):
            pr_number = str(args[2])
            if pr_number == "11":
                return {"state": "MERGED", "url": "https://example.test/pr/11"}
            raise AssertionError(f"unexpected pr view args: {args}")
        if args[:2] == ("pr", "list"):
            return []
        raise AssertionError(f"unexpected gh_json args: {args}")

    def fake_gh_command(*args: Any, **kwargs: Any) -> str:
        gh_calls.append(tuple(args))
        if args[:2] == ("pr", "create"):
            return "https://example.test/pull/22"
        raise AssertionError(f"unexpected gh_command args: {args}")

    def fake_git_command(*args: Any, **kwargs: Any) -> str:
        if args[:1] == ("fetch",):
            return ""
        if args[:2] == ("rev-list", "--count"):
            return "2"
        raise AssertionError(f"unexpected git_command args: {args}")

    def fake_write_status(state: dict[str, Any], message: str) -> None:
        status_messages.append(message)

    loop.get_github_flow = fake_get_github_flow
    loop.gh_json = fake_gh_json
    loop.gh_command = fake_gh_command
    loop.git_command = fake_git_command
    loop.write_github_automation_status = fake_write_status
    try:
        result = loop.sync_release_pr(loop_state, release_contract)
    finally:
        loop.get_github_flow = original_get_flow
        loop.gh_json = original_gh_json
        loop.gh_command = original_gh_command
        loop.git_command = original_git_command
        loop.write_github_automation_status = original_write_status

    assert result.ok is True
    assert result.release_pr_number == 22
    assert result.status == "release_pr_created"
    assert result.report_to_discord is True
    assert result.record_in_journal is True
    assert loop_state["github_flow"]["status"] == "release_pr_open"
    assert status_messages
    assert any(call[:2] == ("pr", "create") for call in gh_calls)
    assert not any(call[:2] == ("pr", "merge") for call in gh_calls)


def run_manual_release_reentry_smoke(release_contract: loop.AgentsContract) -> None:
    loop_state: dict[str, Any] = {
        "github_flow": {
            "pr_number": 11,
            "issue_number": 7,
            "release_pr_number": 22,
            "release_pr_url": "https://example.test/pull/22",
        }
    }
    gh_calls: list[tuple[Any, ...]] = []
    status_messages: list[str] = []

    original_get_flow = loop.get_github_flow
    original_gh_json = loop.gh_json
    original_gh_command = loop.gh_command
    original_git_command = loop.git_command
    original_write_status = loop.write_github_automation_status

    def fake_get_github_flow(state: dict[str, Any]) -> dict[str, Any]:
        return state.setdefault("github_flow", {})

    def fake_gh_json(*args: Any, **kwargs: Any) -> Any:
        if args[:2] == ("pr", "view") and str(args[2]) == "22":
            return {"state": "OPEN", "url": "https://example.test/pull/22"}
        raise AssertionError(f"unexpected gh_json args: {args}")

    def fake_gh_command(*args: Any, **kwargs: Any) -> str:
        gh_calls.append(tuple(args))
        raise AssertionError(f"unexpected gh_command args: {args}")

    def fake_git_command(*args: Any, **kwargs: Any) -> str:
        raise AssertionError(f"unexpected git_command args: {args}")

    def fake_write_status(state: dict[str, Any], message: str) -> None:
        status_messages.append(message)

    loop.get_github_flow = fake_get_github_flow
    loop.gh_json = fake_gh_json
    loop.gh_command = fake_gh_command
    loop.git_command = fake_git_command
    loop.write_github_automation_status = fake_write_status
    try:
        result = loop.sync_release_pr(loop_state, release_contract)
    finally:
        loop.get_github_flow = original_get_flow
        loop.gh_json = original_gh_json
        loop.gh_command = original_gh_command
        loop.git_command = original_git_command
        loop.write_github_automation_status = original_write_status

    assert result.ok is False
    assert result.release_pr_number == 22
    assert result.status == "release_pr_open"
    assert result.report_to_discord is False
    assert result.record_in_journal is True
    assert loop_state["github_flow"]["status"] == "release_pr_open"
    assert status_messages
    assert not gh_calls


def run_release_reporting_smoke() -> None:
    posts: list[dict[str, str]] = []
    console_logs: list[tuple[str, str]] = []
    github_notes: list[str] = []

    original_post_message = loop.post_message
    original_emit_console = loop.emit_console

    def fake_post_message(
        username: str,
        content: str,
        meeting_id: str,
        phase: str,
        trigger_id: str,
        thread_id: str | None,
        source: str = "agent",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        posts.append(
            {
                "username": username,
                "content": content,
                "meeting_id": meeting_id,
                "phase": phase,
                "trigger_id": trigger_id,
                "thread_id": thread_id or "",
            }
        )

    def fake_emit_console(phase: str, message: str) -> None:
        console_logs.append((phase, message))

    created_result = loop.GitHubFlowResult(
        True,
        "Release PR #22를 만들고 main 병합은 사용자 대기 상태로 둔다.",
        release_pr_number=22,
        release_pr_url="https://example.test/pull/22",
        status="release_pr_created",
        report_to_discord=True,
        record_in_journal=True,
    )
    already_open_result = loop.GitHubFlowResult(
        False,
        "Release PR #22가 이미 열려 있고 main 병합은 사용자 대기 상태다.",
        release_pr_number=22,
        release_pr_url="https://example.test/pull/22",
        status="release_pr_open",
        report_to_discord=False,
        record_in_journal=True,
    )
    trigger = {"id": "trigger-1", "thread_id": "thread-1"}

    loop.post_message = fake_post_message
    loop.emit_console = fake_emit_console
    try:
        loop.handle_release_pr_result(created_result, "meeting-1", trigger, github_notes)
        loop.handle_release_pr_result(already_open_result, "meeting-1", trigger, github_notes)
    finally:
        loop.post_message = original_post_message
        loop.emit_console = original_emit_console

    assert github_notes == [created_result.detail, already_open_result.detail]
    assert len(posts) == 1
    assert posts[0]["phase"] == "github_release_pr"
    assert "사용자 대기" in posts[0]["content"]
    assert already_open_result.detail in [message for phase, message in console_logs if phase == "github"]


def run_release_sync_wrapper_smoke(release_contract: loop.AgentsContract) -> None:
    posts: list[dict[str, str]] = []
    original_sync_release_pr = loop.sync_release_pr
    original_post_message = loop.post_message

    created_result = loop.GitHubFlowResult(
        True,
        "Release PR #33을 만들고 main 병합은 사용자 대기 상태로 둔다.",
        release_pr_number=33,
        release_pr_url="https://example.test/pull/33",
        status="release_pr_created",
        report_to_discord=True,
        record_in_journal=True,
    )

    def fake_sync_release_pr(loop_state: dict[str, Any], contract: loop.AgentsContract) -> loop.GitHubFlowResult:
        assert contract == release_contract
        return created_result

    def fake_post_message(
        username: str,
        content: str,
        meeting_id: str,
        phase: str,
        trigger_id: str,
        thread_id: str | None,
        source: str = "agent",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        posts.append(
            {
                "username": username,
                "content": content,
                "meeting_id": meeting_id,
                "phase": phase,
                "trigger_id": trigger_id,
                "thread_id": thread_id or "",
            }
        )

    loop.sync_release_pr = fake_sync_release_pr
    loop.post_message = fake_post_message
    try:
        result = loop.sync_and_report_release_pr(
            {"github_flow": {"issue_number": 1}},
            release_contract,
            meeting_id="github-release-sync",
            trigger={"id": "loop-startup-release-sync", "thread_id": None},
            github_notes=[],
        )
    finally:
        loop.sync_release_pr = original_sync_release_pr
        loop.post_message = original_post_message

    assert result == created_result
    assert len(posts) == 1
    assert posts[0]["trigger_id"] == "loop-startup-release-sync"
    assert posts[0]["phase"] == "github_release_pr"
    assert "사용자 대기" in posts[0]["content"]


def main() -> int:
    contract = loop.parse_agents_contract()
    release_contract = replace(
        contract,
        enable_github_automation=True,
        release_to_main_policy=loop.RELEASE_TO_MAIN_PR_ONLY_POLICY,
    )

    run_manual_release_creation_smoke(release_contract)
    run_manual_release_reentry_smoke(release_contract)
    run_release_reporting_smoke()
    run_release_sync_wrapper_smoke(release_contract)

    print("release PR manual merge policy smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
