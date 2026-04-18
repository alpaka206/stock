from __future__ import annotations

import omx_autonomous_loop as loop


def main() -> int:
    executor_output = {
        "role": "executor",
        "status": "done",
        "summary": "운영 채널에서 release 보고가 재진입 전후 1건으로 유지됐고 develop -> main은 PR 생성만 확인됐으며 merge는 하지 않았다.",
        "proposed_action": "이번 확인은 운영 검증 1차 범위만 종료한다.",
        "followups": ["다음에는 /overview 초기 지연 재현으로 이어간다."],
    }

    result = loop.build_verifier_output(executor_output, True, "ok")

    assert result["status"] == "pass"
    assert "release 보고가 재진입 전후 1건" in result["summary"]
    assert "PR 생성만 확인됐으며 merge는 하지 않았다" in result["team_message"]
    assert "운영 검증 1차 범위만 종료한다" in result["team_message"]
    assert result["proposed_action"] == "다음에는 /overview 초기 지연 재현으로 이어간다."
    assert result["question_for_next"] == "다음에는 /overview 초기 지연 재현으로 이어간다."
    assert result["reply_to"] == ["executor"]

    print("verifier output scope smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
