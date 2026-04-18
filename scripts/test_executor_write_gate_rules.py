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

    assert module.is_allowed_executor_path(".gitignore") is True
    assert module.is_allowed_executor_path(".vscode/settings.json") is True
    assert module.is_allowed_executor_path(".vscode/tasks.json") is True
    assert module.is_allowed_executor_path("plugins/stock-omx-loop/.codex-plugin/plugin.json") is True
    assert module.is_allowed_executor_path("plugins/stock-omx-loop/skills/stock-discord-loop/SKILL.md") is True
    assert module.is_allowed_executor_path("stock.code-workspace") is True

    assert module.is_forbidden_executor_path("omx_discord_bridge/.env.example") is False
    assert module.is_forbidden_executor_path("apps/web/.env.example") is False
    assert module.is_forbidden_executor_path("apps/web/.env.local") is True
    assert module.is_forbidden_executor_path(".venv/Scripts/python.exe") is True
    assert module.is_allowed_executor_path("secrets/api.key") is False

    print("executor write gate rule tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
