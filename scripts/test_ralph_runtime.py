from __future__ import annotations

import tempfile
from pathlib import Path

import ralph_runtime


def main() -> int:
    runtime = ralph_runtime.build_runtime(Path(__file__).resolve().parents[1])
    assert runtime["bridge_host"] == "127.0.0.1"
    assert runtime["bridge_port"] == 8787
    assert runtime["ascii_workspace_drive"] == "X:"
    assert runtime["state_dir"].endswith(".omx\\state") or runtime["state_dir"].endswith(".omx/state")

    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp) / "demo"
        repo_root.mkdir(parents=True, exist_ok=True)
        (repo_root / ".ralph-loop.yml").write_text(
            (
                'project:\n'
                '  name: "demo"\n'
                'runtime:\n'
                '  bridge_host: "127.0.0.1"\n'
                '  bridge_port: 9911\n'
                '  ascii_workspace_drive: "Y:"\n'
            ),
            encoding="utf-8",
        )
        override_runtime = ralph_runtime.build_runtime(repo_root)
        assert override_runtime["bridge_port"] == 9911
        assert override_runtime["ascii_workspace_drive"] == "Y:"

    print("ralph runtime smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
