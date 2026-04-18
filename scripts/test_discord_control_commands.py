from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "omx_discord_bridge"))

import discord_omx_bridge as bridge


def main() -> int:
    command = bridge.parse_ralph_command("/ralph status")
    assert command == {"action": "status", "value": ""}

    command = bridge.parse_ralph_command("/ralph nudge 기존 API 유지")
    assert command == {"action": "nudge", "value": "기존 API 유지"}

    command = bridge.parse_ralph_command("/ralph goal 결제 페이지 완성")
    assert command == {"action": "goal", "value": "결제 페이지 완성"}

    command = bridge.parse_ralph_command("일반 사용자 메시지")
    assert command is None

    print("discord control command smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
