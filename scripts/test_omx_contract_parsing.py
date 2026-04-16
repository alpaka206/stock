from __future__ import annotations

import omx_autonomous_loop as loop


def main() -> int:
    contract = loop.parse_agents_contract()
    assert contract.primary_task, "PRIMARY_TASK must not be empty"
    assert contract.min_exit_condition, "MIN_EXIT_CONDITION must not be empty"
    assert contract.required_docs, "required_docs must not be empty"
    assert contract.required_docs[0] == "docs/architecture/page-manifest.yaml"
    assert contract.consensus_order == (
        "planner",
        "critic",
        "researcher",
        "architect",
        "executor",
        "verifier",
    )

    backlog_text = loop.read_text(loop.BACKLOG_FILE)
    backlog_action = loop.parse_backlog_first_unchecked(backlog_text)
    assert backlog_action == "실제 Discord 채널에서 허용 사용자 메시지 1건으로 latest-only 처리 검증"

    flat_backlog = "# BACKLOG\n\n- [ ] 첫 번째 작업\n- [ ] 두 번째 작업\n"
    assert loop.parse_backlog_first_unchecked(flat_backlog) == "첫 번째 작업"

    legacy_backlog = "# BACKLOG\n\n## P0\n- [ ] 우선 작업\n\n## P1\n- [ ] 다음 작업\n"
    assert loop.parse_backlog_first_unchecked(legacy_backlog) == "우선 작업"

    print("omx contract parsing smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
