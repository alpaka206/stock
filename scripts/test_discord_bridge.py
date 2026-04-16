from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from contextlib import suppress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib import request


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SCRIPT = ROOT / "omx_discord_bridge" / "discord_omx_bridge.py"
CONVERSATION_LOG = ROOT / ".omx" / "state" / "TEAM_CONVERSATION.jsonl"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class CaptureHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            payload = {"_raw": raw_body}
        self.server.payloads.append({"path": self.path, "payload": payload})  # type: ignore[attr-defined]
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def wait_for_health(port: int, timeout_seconds: float = 20.0) -> None:
    deadline = time.time() + timeout_seconds
    url = f"http://127.0.0.1:{port}/health"
    last_error = "bridge did not respond"
    while time.time() < deadline:
        try:
            with request.urlopen(url, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("ok") is True:
                return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(0.25)
    raise RuntimeError(last_error)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=15) as response:
        body = response.read().decode("utf-8")
    return json.loads(body or "{}")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wait_for_entries(meeting_id: str, expected_phases: list[str], timeout_seconds: float = 10.0) -> list[dict[str, Any]]:
    deadline = time.time() + timeout_seconds
    latest_entries: list[dict[str, Any]] = []
    while time.time() < deadline:
        latest_entries = [
            entry
            for entry in read_jsonl(CONVERSATION_LOG)
            if entry.get("meeting_id") == meeting_id
        ]
        phases = [str(entry.get("phase", "")) for entry in latest_entries]
        if phases == expected_phases:
            return latest_entries
        time.sleep(0.2)
    raise RuntimeError(f"unexpected phase order: {[str(entry.get('phase', '')) for entry in latest_entries]!r}")


def main() -> int:
    webhook_port = pick_port()
    bridge_port = pick_port()
    capture_server = ThreadingHTTPServer(("127.0.0.1", webhook_port), CaptureHandler)
    capture_server.payloads = []  # type: ignore[attr-defined]
    capture_thread = threading.Thread(target=capture_server.serve_forever, daemon=True, name="discord-webhook-capture")
    capture_thread.start()

    meeting_id = f"bridge-smoke-{uuid.uuid4().hex[:8]}"
    phase_order = ["coordinator", "planner", "critic", "researcher", "architect", "executor", "verifier"]
    messages = [
        (
            "coordinator",
            "Discord 회의 브리지 스모크를 시작합니다. 역할 응답과 메타데이터가 함께 남는지 확인합니다.",
            {},
        ),
        (
            "planner",
            "이번 스모크의 목표는 최신 지시를 기준으로 회의 로그와 전달 메타데이터가 안정적으로 남는지 확인하는 것입니다.",
            {
                "reply_to": ["user"],
                "team_message": "사용자 지시를 기준으로 회의를 시작하고, 응답 연결 정보까지 같이 남기는지 먼저 확인하겠습니다.",
                "status": "done",
            },
        ),
        (
            "critic",
            "회의 본문만 맞고 reply_to나 team_message가 빠지면 실제 운영에서 추적이 어렵습니다.",
            {
                "reply_to": ["planner"],
                "team_message": "planner 방향에는 동의합니다. 이번에는 메타데이터 보존 여부를 더 엄격하게 보겠습니다.",
                "status": "done",
            },
        ),
        (
            "researcher",
            "브리지 로그와 로컬 TEAM_CONVERSATION 로그를 같이 보면 전달 경로를 빠르게 검증할 수 있습니다.",
            {
                "reply_to": ["critic", "planner"],
                "team_message": "연결 로그를 같이 남겨야 이후 실패 원인도 빠르게 좁힐 수 있습니다.",
                "status": "done",
            },
        ),
        (
            "architect",
            "Webhook 전달과 로컬 로그 저장을 한 번의 /event 호출로 묶는 현재 구조는 스모크 테스트에 적합합니다.",
            {
                "reply_to": ["researcher"],
                "team_message": "좋습니다. 이번 스모크는 Discord 가독성과 메타데이터 보존만 집중 검증하겠습니다.",
                "status": "done",
            },
        ),
        (
            "executor",
            "이 단계에서는 executor 메타데이터가 로그에 그대로 남는지와 전달 본문이 보이는지만 확인하면 충분합니다.",
            {
                "reply_to": ["architect", "critic"],
                "team_message": "executor는 reply_to와 team_message가 TEAM_CONVERSATION에 그대로 남는지 확인 포인트를 잡겠습니다.",
                "changed_files": ["scripts/omx_autonomous_loop.py", "omx_discord_bridge/discord_omx_bridge.py"],
                "status": "done",
            },
        ),
        (
            "verifier",
            "현재 단계에서는 Discord 브리지 전달과 TEAM_CONVERSATION 메타데이터 보존이 모두 통과하면 충분합니다.",
            {
                "reply_to": ["executor"],
                "team_message": "좋습니다. 이번 스모크는 Discord 전달과 메타데이터 보존만 우선 통과시키겠습니다.",
                "verification": ["metadata round-trip pass"],
                "status": "done",
            },
        ),
    ]

    bridge_process: subprocess.Popen[str] | None = None
    with TemporaryDirectory(prefix="discord-bridge-smoke-") as temp_dir:
        env_file = Path(temp_dir) / ".env.discord"
        env_file.write_text(
            f"DISCORD_WEBHOOK_URL=http://127.0.0.1:{webhook_port}/webhook\n",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["DISCORD_ENV_FILE"] = str(env_file)
        env["DISCORD_BRIDGE_PORT"] = str(bridge_port)
        env["DISCORD_POLL_INTERVAL_SECONDS"] = "3600"

        bridge_process = subprocess.Popen(
            [sys.executable, str(BRIDGE_SCRIPT)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        try:
            wait_for_health(bridge_port)
            for role, content, metadata in messages:
                response = post_json(
                    f"http://127.0.0.1:{bridge_port}/event",
                    {
                        "username": role,
                        "content": content,
                        "meeting_id": meeting_id,
                        "phase": role,
                        "trigger_id": meeting_id,
                        "metadata": metadata,
                    },
                )
                ensure(response.get("ok") is True, f"/event failed for {role}: {response}")

            entries = wait_for_entries(meeting_id, phase_order)

            executor_entry = next((entry for entry in entries if entry.get("phase") == "executor"), None)
            ensure(executor_entry is not None, "executor entry missing from TEAM_CONVERSATION log")
            ensure(
                executor_entry.get("reply_to") == ["architect", "critic"],
                f"executor reply_to missing or wrong: {executor_entry.get('reply_to')!r}",
            )
            ensure(
                executor_entry.get("team_message")
                == "executor는 reply_to와 team_message가 TEAM_CONVERSATION에 그대로 남는지 확인 포인트를 잡겠습니다.",
                "executor team_message missing from TEAM_CONVERSATION log",
            )

            webhook_payloads = list(capture_server.payloads)  # type: ignore[attr-defined]
            ensure(len(webhook_payloads) == len(messages), f"unexpected webhook payload count: {len(webhook_payloads)}")
            webhook_usernames = [str(item["payload"].get("username", "")) for item in webhook_payloads]
            ensure(webhook_usernames == phase_order, f"unexpected webhook usernames: {webhook_usernames!r}")
        finally:
            if bridge_process.poll() is None:
                bridge_process.terminate()
                with suppress(subprocess.TimeoutExpired):
                    bridge_process.wait(timeout=5)
            if bridge_process.poll() is None:
                bridge_process.kill()
                bridge_process.wait(timeout=5)

    capture_server.shutdown()
    capture_server.server_close()
    capture_thread.join(timeout=5)

    if bridge_process is not None and bridge_process.returncode not in (0, 1, None, -15):
        output = bridge_process.stdout.read().strip() if bridge_process.stdout else ""
        raise RuntimeError(f"bridge exited unexpectedly: {bridge_process.returncode}\n{output}")

    print("Discord bridge smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
