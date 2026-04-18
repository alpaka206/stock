from __future__ import annotations

import omx_autonomous_loop as loop


def main() -> int:
    contract = loop.parse_agents_contract()
    assert contract.primary_task, "goal must not be empty"
    assert contract.min_exit_condition, "minimum_done must not be empty"
    assert contract.required_docs, "required_docs must not be empty"
    assert contract.required_docs[0] == ".ralph-loop.yml"
    assert "docs/design/stock-reference-blueprint.md" in contract.required_docs
    assert "docs/design/chart-pattern-atlas.md" in contract.required_docs
    assert "docs/prompts/09-완성형-주식-분석-사이트.md" in contract.required_docs
    assert contract.consensus_order == (
        "planner",
        "critic",
        "researcher",
        "architect",
        "executor",
        "verifier",
    )
    assert contract.git_base_branch == "develop_loop"
    assert contract.issue_branch_prefix == "issue"
    assert set(contract.protected_branches) >= {"main", "develop", "develop_loop"}
    assert contract.release_to_main_policy == "disabled"
    assert contract.runtime_bridge_host == "127.0.0.1"
    assert contract.runtime_bridge_port == 8787
    assert contract.runtime_ascii_workspace_drive == "X:"

    flat_backlog = "# BACKLOG\n\n- [ ] 첫 번째 작업\n- [ ] 두 번째 작업\n"
    assert loop.parse_backlog_first_unchecked(flat_backlog) == "첫 번째 작업"

    legacy_backlog = "# BACKLOG\n\n## P0\n- [ ] 우선 작업\n\n## P1\n- [ ] 다음 작업\n"
    assert loop.parse_backlog_first_unchecked(legacy_backlog) == "우선 작업"

    print("omx contract parsing smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
