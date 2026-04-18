from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "omx_autonomous_loop.py"


def load_module():
    spec = importlib.util.spec_from_file_location("omx_autonomous_loop", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load omx_autonomous_loop module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()

    assert module.normalize_discord_mode("all") == "all"
    assert module.normalize_discord_mode("signal-only") == "signal-only"
    assert module.normalize_discord_mode("local-only") == "local-only"
    assert module.normalize_discord_mode("unexpected-value") == "all"

    assert module.should_emit_to_discord("meeting_start", {}, "signal-only") is True
    assert module.should_emit_to_discord("meeting_end", {}, "signal-only") is True
    assert module.should_emit_to_discord("planner", {}, "signal-only") is False
    assert module.should_emit_to_discord("executor", {"needs_human": True}, "signal-only") is True
    assert module.should_emit_to_discord("meeting_end", {}, "local-only") is False
    assert module.should_emit_to_discord("planner", {}, "all") is True

    print("omx discord mode tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
