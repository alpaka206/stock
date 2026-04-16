from __future__ import annotations

from dataclasses import replace
from typing import Any

import omx_autonomous_loop as loop


def main() -> int:
    contract = loop.parse_agents_contract()
    assert (
        contract.release_to_main_policy == loop.RELEASE_TO_MAIN_PR_ONLY_POLICY
    ), f"RELEASE_TO_MAIN_POLICY must be {loop.RELEASE_TO_MAIN_PR_ONLY_POLICY}"

    release_contract = replace(contract, enable_github_automation=True)
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

    assert result.ok is True, "manual release policy should still create a release PR"
    assert result.release_pr_number == 22, "release PR number should come from created PR URL"
    assert "사용자 대기" in result.detail, "release detail should say manual merge is pending"
    assert loop_state["github_flow"]["status"] == "release_pr_open"
    assert status_messages and "사용자 대기" in status_messages[-1]
    assert any(call[:2] == ("pr", "create") for call in gh_calls), "release PR should be created"
    assert not any(call[:2] == ("pr", "merge") for call in gh_calls), "manual release policy must not auto-merge main PRs"

    print("release PR manual merge policy smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
