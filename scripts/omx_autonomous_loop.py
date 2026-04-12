from __future__ import annotations

import json
import os
import re
import subprocess
import textwrap
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from shutil import which
from typing import Any
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
AGENTS_FILE = ROOT / "AGENTS.md"
STATE_DIR = ROOT / ".omx" / "state"
RUNTIME_DIR = ROOT / ".omx" / "runtime"
JOURNAL_DIR = ROOT / ".omx" / "journal"
NEXT_PROMPT_FILE = STATE_DIR / "NEXT_PROMPT.md"
TASK_FILE = STATE_DIR / "TASK.md"
STATE_FILE = STATE_DIR / "STATE.md"
BACKLOG_FILE = STATE_DIR / "BACKLOG.md"
VERIFY_FAILURE_FILE = STATE_DIR / "VERIFY_LAST_FAILURE.md"
DISCORD_STATUS_FILE = STATE_DIR / "DISCORD_STATUS.md"
DISCORD_INBOX_LOG = STATE_DIR / "DISCORD_INBOX.jsonl"
TEAM_CONVERSATION_LOG = STATE_DIR / "TEAM_CONVERSATION.jsonl"
LOOP_STATE_FILE = STATE_DIR / "OMX_LOOP_STATE.json"
LOOP_RUNTIME_STATUS_FILE = RUNTIME_DIR / "omx-loop-status.json"
ROLE_SCHEMA_FILE = ROOT / "scripts" / "omx_role_output.schema.json"


def resolve_workspace_root() -> str:
    override = os.getenv("OMX_WORKSPACE_ROOT", "").strip()
    if override:
        return override

    raw_root = str(ROOT)
    if os.name != "nt" or raw_root.isascii():
        return raw_root

    drive = os.getenv("OMX_ASCII_WORKSPACE_DRIVE", "X:").strip() or "X:"
    if re.fullmatch(r"[A-Za-z]:", drive):
        try:
            subprocess.run(["subst", drive, raw_root], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return f"{drive}\\"
        except Exception:
            pass

    try:
        import ctypes

        buffer = ctypes.create_unicode_buffer(1024)
        written = ctypes.windll.kernel32.GetShortPathNameW(raw_root, buffer, len(buffer))
        if written:
            short_path = buffer.value
            if short_path:
                return short_path
    except Exception:
        pass
    return raw_root


OMX_WORKSPACE_ROOT = resolve_workspace_root()
ROLE_ORDER = ("planner", "critic", "researcher", "architect", "executor", "verifier")
DISCORD_BRIDGE_PORT = int(os.getenv("DISCORD_BRIDGE_PORT", "8787"))
AUTONOMOUS_IDLE_INTERVAL_SECONDS = max(int(os.getenv("OMX_AUTONOMOUS_IDLE_INTERVAL_SECONDS", "300")), 60)
ROLE_TIMEOUT_SECONDS = max(int(os.getenv("OMX_ROLE_TIMEOUT_SECONDS", "900")), 120)
VERIFY_TIMEOUT_SECONDS = max(int(os.getenv("OMX_VERIFY_TIMEOUT_SECONDS", "1800")), 120)
RECENT_CONVERSATION_LIMIT = max(int(os.getenv("OMX_RECENT_CONVERSATION_LIMIT", "16")), 4)
MAX_TRACKED_IDS = 400


def emit_console(phase: str, message: str) -> None:
    print(f"[omx][{iso_now()}][{phase}] {message}", flush=True)


def write_runtime_status(*, status: str, detail: str = "", meeting_id: str = "", role: str = "", trigger: str = "") -> None:
    write_json(
        LOOP_RUNTIME_STATUS_FILE,
        {
            "status": status,
            "detail": detail,
            "meeting_id": meeting_id,
            "role": role,
            "trigger": trigger,
            "updated_at": iso_now(),
        },
    )


def parse_agents_contract() -> AgentsContract:
    text = read_text(AGENTS_FILE)

    def find_value(key: str, default: str = "") -> str:
        match = re.search(rf"^- {re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
        return match.group(1).strip() if match else default

    required_docs: list[str] = []
    in_required_docs = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "?? ?? ??":
            in_required_docs = True
            continue
        if in_required_docs and stripped.startswith("## "):
            break
        if in_required_docs and stripped.startswith("- "):
            required_docs.append(stripped[2:].strip().strip("`").strip())

    consensus_match = re.search(r"`([^`]+)` ??", text)
    return AgentsContract(
        primary_task=find_value("PRIMARY_TASK"),
        min_exit_condition=find_value("MIN_EXIT_CONDITION"),
        auto_continue_policy=find_value("AUTO_CONTINUE_POLICY"),
        release_to_main_policy=find_value("RELEASE_TO_MAIN_POLICY"),
        required_docs=tuple(required_docs),
        consensus_order=consensus_match.group(1).strip() if consensus_match else "planner -> critic -> architect -> executor",
    )


def build_agents_excerpt(contract: AgentsContract) -> str:
    lines = [
        f"- PRIMARY_TASK: {contract.primary_task}",
        f"- MIN_EXIT_CONDITION: {contract.min_exit_condition}",
        f"- AUTO_CONTINUE_POLICY: {contract.auto_continue_policy}",
        f"- RELEASE_TO_MAIN_POLICY: {contract.release_to_main_policy}",
        f"- CONSENSUS_ORDER: {contract.consensus_order}",
    ]
    if contract.required_docs:
        lines.append("- REQUIRED_DOCS:")
        lines.extend(f"  - {item}" for item in contract.required_docs)
    return "\n".join(lines)


@dataclass(frozen=True)
class AgentsContract:
    primary_task: str
    min_exit_condition: str
    auto_continue_policy: str
    release_to_main_policy: str
    required_docs: tuple[str, ...]
    consensus_order: str


@dataclass(frozen=True)
class RoleSpec:
    name: str
    goal: str
    sandbox: str
    writable: bool = False


ROLE_SPECS = {
    "planner": RoleSpec("planner", "트리거와 상태 파일을 읽고 이번 iteration의 가장 작은 P0 작업을 고른다.", "read-only"),
    "critic": RoleSpec("critic", "계획의 허점, 정책 위반, 검증 누락을 먼저 잡는다.", "read-only"),
    "researcher": RoleSpec("researcher", "레포와 상태 파일에서 빠진 사실, 관련 파일, 테스트 경로를 보강한다.", "read-only"),
    "architect": RoleSpec("architect", "합의된 작업을 가장 작은 구현 단위와 검증 단위로 나눈다.", "read-only"),
    "executor": RoleSpec("executor", "합의된 최소 작업을 실제로 구현하고 필요한 검증을 먼저 돌린다.", "workspace-write", True),
    "verifier": RoleSpec("verifier", "변경 결과와 검증 로그를 읽고 pass/fail 및 다음 복구 포인트를 정리한다.", "read-only"),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def trim(text: str, limit: int = 3000) -> str:
    normalized = re.sub(r"\s+\n", "\n", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def slugify(value: str) -> str:
    lowered = re.sub(r"[^a-z0-9가-힣]+", "-", value.lower())
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "task"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            items.append(payload)
    return items


def parse_backlog_first_unchecked(text: str) -> str:
    current_section = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            continue
        if current_section == "P0" and stripped.startswith("- [ ] "):
            return stripped[len("- [ ] ") :].strip()
    return ""


def parse_next_prompt_action(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s", stripped):
            return re.sub(r"^\d+\.\s*", "", stripped)
    return ""


def parse_verify_failure(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def recent_conversation(limit: int = RECENT_CONVERSATION_LIMIT) -> list[dict[str, Any]]:
    return load_jsonl(TEAM_CONVERSATION_LOG)[-limit:]


def render_recent_conversation(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- 최근 대화 없음"
    lines: list[str] = []
    for item in items:
        speaker = str(item.get("role") or item.get("author") or item.get("source") or "unknown")
        content = trim(str(item.get("content", "")), 240)
        meeting_id = str(item.get("meeting_id", "")).strip()
        if meeting_id:
            lines.append(f"- {speaker} [{meeting_id}]: {content}")
        else:
            lines.append(f"- {speaker}: {content}")
    return "\n".join(lines)


def load_loop_state() -> dict[str, Any]:
    default = {
        "iteration": 0,
        "meeting_counter": 0,
        "handled_discord_message_ids": [],
        "last_autonomous_cycle_at": "",
        "last_failure_signature": "",
        "failure_streak": 0,
        "last_result": "",
        "last_meeting_id": "",
        "last_next_action": "",
        "pending_followup": {},
    }
    payload = load_json(LOOP_STATE_FILE, default)
    if not isinstance(payload, dict):
        return default
    merged = default | payload
    if not isinstance(merged.get("handled_discord_message_ids"), list):
        merged["handled_discord_message_ids"] = []
    if not isinstance(merged.get("pending_followup"), dict):
        merged["pending_followup"] = {}
    return merged


def save_loop_state(payload: dict[str, Any]) -> None:
    handled = payload.get("handled_discord_message_ids", [])
    if isinstance(handled, list):
        payload["handled_discord_message_ids"] = handled[-MAX_TRACKED_IDS:]
    if not isinstance(payload.get("pending_followup"), dict):
        payload["pending_followup"] = {}
    write_json(LOOP_STATE_FILE, payload)


def select_trigger(loop_state: dict[str, Any], contract: AgentsContract) -> dict[str, Any] | None:
    handled_ids = set(str(item) for item in loop_state.get("handled_discord_message_ids", []))
    for item in reversed(load_jsonl(DISCORD_INBOX_LOG)):
        message_id = str(item.get("message_id", "")).strip()
        content = str(item.get("content", "")).strip()
        if not message_id or not content or message_id in handled_ids:
            continue
        return {
            "id": f"discord-{message_id}",
            "kind": "discord_user",
            "message_id": message_id,
            "author": str(item.get("author", "unknown")),
            "content": content,
            "channel_id": str(item.get("channel_id", "")),
            "thread_id": str(item.get("thread_id", "")).strip() or None,
            "label": f"Discord ??? ??: {content}",
        }

    verify_failure = parse_verify_failure(read_text(VERIFY_FAILURE_FILE))
    if verify_failure.get("status") == "active":
        failing_command = verify_failure.get("failing_command", "unknown")
        symptom = verify_failure.get("symptom", "")
        return {
            "id": f"verify-{slugify(failing_command + '-' + symptom)}",
            "kind": "verify_failure",
            "content": f"?? ?? ??? ????. failing_command={failing_command}, symptom={symptom}",
            "label": f"?? ?? ??: {failing_command}",
        }

    pending_followup = loop_state.get("pending_followup") or {}
    followup_content = str(pending_followup.get("content", "")).strip()
    if followup_content:
        return {
            "id": str(pending_followup.get("id", f"followup-{slugify(followup_content)}")),
            "kind": "followup",
            "content": followup_content,
            "label": f"?? ??: {followup_content}",
            "thread_id": None,
        }

    last_cycle_raw = str(loop_state.get("last_autonomous_cycle_at", "")).strip()
    if last_cycle_raw:
        try:
            last_cycle = datetime.fromisoformat(last_cycle_raw.replace("Z", "+00:00"))
        except ValueError:
            last_cycle = utc_now() - timedelta(seconds=AUTONOMOUS_IDLE_INTERVAL_SECONDS + 1)
    else:
        last_cycle = utc_now() - timedelta(seconds=AUTONOMOUS_IDLE_INTERVAL_SECONDS + 1)

    if (utc_now() - last_cycle).total_seconds() < AUTONOMOUS_IDLE_INTERVAL_SECONDS:
        return None

    backlog_action = parse_backlog_first_unchecked(read_text(BACKLOG_FILE))
    if backlog_action:
        return {
            "id": f"autonomous-{slugify(backlog_action)}",
            "kind": "autonomous_backlog",
            "content": backlog_action,
            "label": f"?? ??: {backlog_action}",
        }

    prompt_action = parse_next_prompt_action(read_text(NEXT_PROMPT_FILE))
    if prompt_action:
        return {
            "id": f"next-prompt-{slugify(prompt_action)}",
            "kind": "next_prompt",
            "content": prompt_action,
            "label": f"?? ?? ??: {prompt_action}",
        }

    if contract.primary_task:
        return {
            "id": "agents-primary-task",
            "kind": "agents_primary_task",
            "content": contract.primary_task,
            "label": "AGENTS ?? ?? ??",
        }
    return None


def bridge_url(path: str) -> str:
    return f"http://127.0.0.1:{DISCORD_BRIDGE_PORT}{path}"


def load_discord_env_values() -> dict[str, str]:
    env_path = Path(os.getenv("DISCORD_ENV_FILE", str(ROOT / "omx_discord_bridge" / ".env.discord")))
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def append_local_conversation(
    *,
    username: str,
    content: str,
    source: str,
    meeting_id: str,
    phase: str,
    trigger_id: str,
    thread_id: str | None = None,
) -> None:
    append_jsonl(
        TEAM_CONVERSATION_LOG,
        {
            "source": source,
            "role": username,
            "content": content,
            "meeting_id": meeting_id,
            "phase": phase,
            "trigger_id": trigger_id,
            "thread_id": thread_id or "",
            "created_at": iso_now(),
        },
    )


def direct_discord_webhook_post(*, webhook_url: str, content: str, username: str, thread_id: str | None) -> bool:
    if not webhook_url:
        return False
    target_url = webhook_url
    if thread_id:
        separator = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{separator}{parse.urlencode({'thread_id': thread_id})}"
    payload = json.dumps(
        {
            "content": content,
            "username": username,
            "allowed_mentions": {"parse": []},
        }
    ).encode("utf-8")
    req = request.Request(target_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=15) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def post_message(
    *,
    username: str,
    content: str,
    meeting_id: str,
    phase: str,
    trigger_id: str,
    thread_id: str | None = None,
    source: str = "agent",
) -> None:
    payload = json.dumps(
        {
            "username": username,
            "content": content,
            "thread_id": thread_id,
            "meeting_id": meeting_id,
            "phase": phase,
            "source": source,
            "trigger_id": trigger_id,
        }
    ).encode("utf-8")
    try:
        req = request.Request(bridge_url("/event"), data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=15) as response:
            if 200 <= response.status < 300:
                return
    except error.URLError:
        pass

    env_values = load_discord_env_values()
    sent = direct_discord_webhook_post(
        webhook_url=env_values.get("DISCORD_WEBHOOK_URL", "").strip(),
        content=content,
        username=username,
        thread_id=thread_id,
    )
    append_local_conversation(
        username=username,
        content=content,
        source=source if sent else f"{source}_local",
        meeting_id=meeting_id,
        phase=phase,
        trigger_id=trigger_id,
        thread_id=thread_id,
    )


def sync_discord_replies() -> None:
    try:
        req = request.Request(bridge_url("/sync-replies"), data=b"{}", method="POST")
        with request.urlopen(req, timeout=15):
            return
    except Exception:
        return


def find_omx_exec() -> str:
    for candidate in ("omx.cmd", str(Path.home() / "AppData" / "Roaming" / "npm" / "omx.cmd")):
        resolved = which(candidate)
        if resolved:
            return resolved
    raise FileNotFoundError("omx.cmd not found")


def find_bash() -> str:
    candidates = [
        os.getenv("OMX_BASH", "").strip(),
        r"C:\Program Files\Git\bin\bash.exe",
        which("bash.exe") or "",
        which("bash") or "",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError("bash executable not found")


def build_state_excerpt() -> str:
    return "\n\n".join(
        [
            "## TASK.md\n" + trim(read_text(TASK_FILE), 1600),
            "## STATE.md\n" + trim(read_text(STATE_FILE), 1600),
            "## BACKLOG.md\n" + trim(read_text(BACKLOG_FILE), 1600),
            "## NEXT_PROMPT.md\n" + trim(read_text(NEXT_PROMPT_FILE), 1600),
            "## VERIFY_LAST_FAILURE.md\n" + trim(read_text(VERIFY_FAILURE_FILE), 1000),
            "## DISCORD_STATUS.md\n" + trim(read_text(DISCORD_STATUS_FILE), 1200),
        ]
    )


def build_role_prompt(*, role: RoleSpec, trigger: dict[str, Any], meeting_id: str, prior_outputs: list[dict[str, Any]], contract: AgentsContract) -> str:
    prior_sections: list[str] = []
    for item in prior_outputs:
        prior_sections.append(
            textwrap.dedent(
                f"""
                ### {item['role']}
                - status: {item['status']}
                - summary: {item['summary']}
                - rationale: {item['rationale']}
                - proposed_action: {item['proposed_action']}
                - risks: {', '.join(item['risks']) if item['risks'] else '??'}
                - verification: {', '.join(item['verification']) if item['verification'] else '??'}
                - changed_files: {', '.join(item['changed_files']) if item['changed_files'] else '??'}
                - followups: {', '.join(item['followups']) if item['followups'] else '??'}
                """
            ).strip()
        )

    permission_text = (
        "?? ??? ?? ?? ??? ?? ??? ????. ?? ???? ???? ?? ????."
        if role.writable
        else "?? ??? read-only?. shell, browser, MCP, ?? ??? ???? ?? ??? ????? ????."
    )

    return textwrap.dedent(
        f"""
        ?? OMX ?? ??? `{role.name}` ????.
        ??: {role.goal}

        AGENTS.md ??:
        {build_agents_excerpt(contract)}

        ?? ??:
        - AGENTS.md? PRIMARY_TASK, MIN_EXIT_CONDITION, AUTO_CONTINUE_POLICY? source of truth? ???.
        - ?? ?? ??? ??? ???? ???? ???? ?? ??? ??? ???.
        - ??? ???? ???? ?? ? ???? ???, ?? ??? PRIMARY_TASK? MIN_EXIT_CONDITION? ???.
        - ??? ???? ??.
        - ??, ??, ?? ??, ?? ??? ???? ???.
        - ?? ??? JSON Schema? ??? ???? ??.
        - needs_human? ?? ?? ??? ??? ???? true? ??.
        - changed_files? ?? ?? ???? ??? ??? ???.
        - read-only ??? changed_files? ??? ??.
        - {permission_text}
        - read-only ??? ?? ??? ???? tool ?? ?? risks, verification, followups? ???.

        ?? ??:
        - meeting_id: {meeting_id}
        - trigger_kind: {trigger['kind']}
        - trigger_label: {trigger['label']}
        - trigger_content: {trigger['content']}

        ?? ?? ??:
        {chr(10).join(f'- {item}' for item in contract.required_docs) if contract.required_docs else '- ??'}

        ?? ??:
        {render_recent_conversation(recent_conversation())}

        ?? ?? ??:
        {build_state_excerpt()}

        ?? ?? ??:
        {chr(10).join(prior_sections) if prior_sections else '- ?? ??'}

        ??? ??:
        - planner: ?? ?? ?? ?? ??? ?? ??? ???.
        - critic: ?? ??, ?? ??, ?? ??? ?? ????.
        - researcher: ??? ????? ?? ??? ?? ??/?? ??? ????.
        - architect: ?? ??? ?? ??? ?? ?? ??? ???.
        - executor: ??? ?? ??? ???? ?? ????.
        - verifier: ?? ??? MIN_EXIT_CONDITION? ??? ?????? ???? ?? follow-up meeting ??? ???.
        """
    ).strip()


def run_role(*, role: RoleSpec, trigger: dict[str, Any], meeting_id: str, prior_outputs: list[dict[str, Any]], contract: AgentsContract) -> dict[str, Any]:
    emit_console(role.name, f"run start trigger={trim(trigger['label'], 100)}")
    write_runtime_status(status="role_running", detail=trim(trigger['label'], 160), meeting_id=meeting_id, role=role.name, trigger=trigger['kind'])

    omx_exec = find_omx_exec()
    output_file = RUNTIME_DIR / f"{meeting_id}-{role.name}-output.json"
    log_file = RUNTIME_DIR / f"{meeting_id}-{role.name}.log"
    args = [
        omx_exec,
        "exec",
        "--cd",
        OMX_WORKSPACE_ROOT,
        "--ephemeral",
        "--color",
        "never",
        "--output-schema",
        str(ROLE_SCHEMA_FILE),
        "-o",
        str(output_file),
        "-",
    ]
    if role.writable:
        args.insert(2, "--full-auto")
    else:
        args[2:2] = ["--sandbox", role.sandbox]

    prompt = build_role_prompt(role=role, trigger=trigger, meeting_id=meeting_id, prior_outputs=prior_outputs, contract=contract)
    with log_file.open("w", encoding="utf-8") as log_handle:
        completed = subprocess.run(
            args,
            input=prompt.encode("utf-8"),
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            timeout=ROLE_TIMEOUT_SECONDS,
            check=False,
        )

    if completed.returncode != 0:
        raise RuntimeError(f"{role.name} failed with exit={completed.returncode}: {trim(read_text(log_file), 1200)}")

    try:
        payload = json.loads(read_text(output_file))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{role.name} returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{role.name} returned non-object payload")

    payload["role"] = role.name
    for key in ("risks", "verification", "changed_files", "followups"):
        if not isinstance(payload.get(key), list):
            payload[key] = []
    payload["summary"] = str(payload.get("summary", "")).strip()
    payload["rationale"] = str(payload.get("rationale", "")).strip()
    payload["proposed_action"] = str(payload.get("proposed_action", "")).strip()
    payload["status"] = str(payload.get("status", "")).strip() or "continue"
    try:
        payload["confidence"] = float(payload.get("confidence", 0))
    except (TypeError, ValueError):
        payload["confidence"] = 0.0
    payload["needs_human"] = bool(payload.get("needs_human", False))

    log_text = read_text(log_file)
    if "CreateProcessWithLogonW failed" in log_text:
        emit_console(role.name, "internal tool attempt failed; continuing from prompt context")

    emit_console(role.name, f"done status={payload['status']} needs_human={payload['needs_human']} next={trim(payload['proposed_action'], 100)}")
    write_runtime_status(status="role_done", detail=trim(payload['summary'], 160), meeting_id=meeting_id, role=role.name, trigger=trigger['kind'])
    return payload


def format_role_message(*, role: RoleSpec, trigger: dict[str, Any], meeting_id: str, prior_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    omx_exec = find_omx_exec()
    output_file = RUNTIME_DIR / f"{meeting_id}-{role.name}-output.json"
    log_file = RUNTIME_DIR / f"{meeting_id}-{role.name}.log"
    args = [
        omx_exec,
        "exec",
        "--cd",
        OMX_WORKSPACE_ROOT,
        "--ephemeral",
        "--color",
        "never",
        "--output-schema",
        str(ROLE_SCHEMA_FILE),
        "-o",
        str(output_file),
        "-",
    ]
    if role.writable:
        args.insert(2, "--full-auto")
    else:
        args[2:2] = ["--sandbox", role.sandbox]

    prompt = build_role_prompt(role=role, trigger=trigger, meeting_id=meeting_id, prior_outputs=prior_outputs)
    with log_file.open("w", encoding="utf-8") as log_handle:
        completed = subprocess.run(
            args,
            input=prompt.encode("utf-8"),
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            timeout=ROLE_TIMEOUT_SECONDS,
            check=False,
        )

    if completed.returncode != 0:
        raise RuntimeError(f"{role.name} failed with exit={completed.returncode}: {trim(read_text(log_file), 1200)}")

    try:
        payload = json.loads(read_text(output_file))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{role.name} returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{role.name} returned non-object payload")

    payload["role"] = role.name
    for key in ("risks", "verification", "changed_files", "followups"):
        if not isinstance(payload.get(key), list):
            payload[key] = []
    payload["summary"] = str(payload.get("summary", "")).strip()
    payload["rationale"] = str(payload.get("rationale", "")).strip()
    payload["proposed_action"] = str(payload.get("proposed_action", "")).strip()
    payload["status"] = str(payload.get("status", "")).strip() or "continue"
    try:
        payload["confidence"] = float(payload.get("confidence", 0))
    except (TypeError, ValueError):
        payload["confidence"] = 0.0
    payload["needs_human"] = bool(payload.get("needs_human", False))
    return payload


def format_role_message(payload: dict[str, Any], meeting_id: str, trigger: dict[str, Any]) -> str:
    risks = "\n".join(f"- {item}" for item in payload["risks"]) if payload["risks"] else "- 없음"
    verification = "\n".join(f"- {item}" for item in payload["verification"]) if payload["verification"] else "- 없음"
    changed_files = "\n".join(f"- {item}" for item in payload["changed_files"]) if payload["changed_files"] else "- 없음"
    followups = "\n".join(f"- {item}" for item in payload["followups"]) if payload["followups"] else "- 없음"
    return textwrap.dedent(
        f"""
        [meeting:{meeting_id}][{payload['role']}]
        트리거: {trigger['label']}
        상태: {payload['status']}
        판단: {payload['summary']}
        근거: {payload['rationale']}
        다음 액션: {payload['proposed_action']}
        리스크:
        {risks}
        검증:
        {verification}
        변경 파일:
        {changed_files}
        후속:
        {followups}
        confidence: {payload['confidence']:.2f}
        """
    ).strip()


def run_bash_script(script_path: Path, *, log_name: str, timeout: int) -> tuple[int, str]:
    bash_exe = find_bash()
    log_file = RUNTIME_DIR / log_name
    with log_file.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            [bash_exe, str(script_path)],
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    return completed.returncode, trim(read_text(log_file), 2000)


def write_verify_failure(*, status: str, failing_command: str, symptom: str, likely_cause: str, next_fix: str) -> None:
    write_text(
        VERIFY_FAILURE_FILE,
        textwrap.dedent(
            f"""\
            # Verify Last Failure

            status: {status}
            failing_command: {failing_command}
            symptom: {symptom}
            likely_cause: {likely_cause}
            remediation_owner: current iteration
            next_fix: {next_fix}
            """
        ),
    )


def run_verify_gate() -> tuple[bool, str]:
    steps = [
        (ROOT / "scripts" / "no_secrets_guard.sh", "scripts/no_secrets_guard.sh", "no-secrets-guard.log", 300),
        (ROOT / "scripts" / "verify_minimal.sh", "scripts/verify_minimal.sh", "verify-last.log", VERIFY_TIMEOUT_SECONDS),
    ]
    logs: list[str] = []
    for script_path, label, log_name, timeout in steps:
        returncode, log_text = run_bash_script(script_path, log_name=log_name, timeout=timeout)
        logs.append(f"$ {label}\n{log_text}")
        if returncode != 0:
            write_verify_failure(
                status="active",
                failing_command=label,
                symptom="verification command returned non-zero",
                likely_cause=f"inspect .omx/runtime/{log_name}",
                next_fix="fix the failing verification item and rerun the same command first",
            )
            return False, "\n\n".join(logs)

    write_verify_failure(status="clear", failing_command="", symptom="", likely_cause="", next_fix="")
    return True, "\n\n".join(logs)


def compute_next_action(role_outputs: list[dict[str, Any]], contract: AgentsContract) -> str:
    if role_outputs:
        last_output = role_outputs[-1]
        for candidate in list(last_output.get("followups", [])) + [last_output.get("proposed_action", "")]:
            candidate_text = str(candidate).strip()
            if candidate_text:
                return candidate_text
    return contract.primary_task or "?? P0 ?? ??"


def schedule_followup(loop_state: dict[str, Any], role_outputs: list[dict[str, Any]], next_action: str, meeting_id: str) -> None:
    if not role_outputs:
        loop_state["pending_followup"] = {}
        return
    last_output = role_outputs[-1]
    normalized = next_action.strip()
    if not normalized or last_output.get("needs_human"):
        loop_state["pending_followup"] = {}
        loop_state["last_next_action"] = normalized
        return
    loop_state["pending_followup"] = {
        "id": f"followup-{slugify(normalized)}",
        "content": normalized,
        "label": f"?? ??: {normalized}",
        "source_meeting_id": meeting_id,
        "created_at": iso_now(),
    }
    loop_state["last_next_action"] = normalized


def write_iteration_journal(
    *,
    iteration: int,
    meeting_id: str,
    trigger: dict[str, Any] | None,
    role_outputs: list[dict[str, Any]],
    verify_ok: bool | None,
    verify_log: str,
    next_action: str,
    note: str,
) -> None:
    changed_files: list[str] = []
    verification_lines: list[str] = []
    for output in role_outputs:
        for path in output.get("changed_files", []):
            if path not in changed_files:
                changed_files.append(path)
        for item in output.get("verification", []):
            if item not in verification_lines:
                verification_lines.append(item)

    if verify_ok is True:
        verification_lines.append("scripts/no_secrets_guard.sh: pass")
        verification_lines.append("scripts/verify_minimal.sh: pass")
    elif verify_ok is False and "guard/verify gate: fail" not in verification_lines:
        verification_lines.append("guard/verify gate: fail")

    journal = textwrap.dedent(
        f"""
        # Loop Iteration {iteration}

        - started_at: {iso_now()}
        - meeting_id: {meeting_id}
        - trigger: {trigger['label'] if trigger else '대기'}
        - note: {note}

        ## 역할 회의 요약
        {chr(10).join(f"- {item['role']}: {item['summary']}" for item in role_outputs) or '- 역할 실행 없음'}

        ## 변경 대상
        {chr(10).join(f"- {item}" for item in changed_files) or '- 없음'}

        ## 검증 결과
        {chr(10).join(f"- {item}" for item in verification_lines) or '- 없음'}

        ## verify 로그 발췌
        ```text
        {verify_log.strip() or '없음'}
        ```

        ## 다음 액션
        - {next_action}
        """
    ).strip() + "\n"
    write_text(JOURNAL_DIR / f"loop-{iteration:04d}.md", journal)


def update_failure_streak(loop_state: dict[str, Any], verify_ok: bool, trigger: dict[str, Any] | None) -> None:
    if verify_ok:
        loop_state["last_failure_signature"] = ""
        loop_state["failure_streak"] = 0
        return
    signature = f"{trigger['kind']}::{trigger['id']}" if trigger else "idle"
    if loop_state.get("last_failure_signature") == signature:
        loop_state["failure_streak"] = int(loop_state.get("failure_streak", 0)) + 1
    else:
        loop_state["last_failure_signature"] = signature
        loop_state["failure_streak"] = 1


def run_meeting(loop_state: dict[str, Any], trigger: dict[str, Any], contract: AgentsContract) -> tuple[list[dict[str, Any]], bool | None, str, str]:
    loop_state["meeting_counter"] = int(loop_state.get("meeting_counter", 0)) + 1
    meeting_id = f"{utc_now().strftime('%Y%m%d-%H%M%S')}-{loop_state['meeting_counter']:04d}"
    loop_state["last_meeting_id"] = meeting_id

    emit_console("meeting", f"start id={meeting_id} trigger={trim(trigger['label'], 120)}")
    write_runtime_status(status="meeting_start", detail=trim(trigger["label"], 160), meeting_id=meeting_id, role="coordinator", trigger=trigger["kind"])
    post_message(
        username="coordinator",
        content=f"[meeting:{meeting_id}] ??. trigger={trigger['label']}",
        meeting_id=meeting_id,
        phase="meeting_start",
        trigger_id=trigger["id"],
        thread_id=trigger.get("thread_id"),
    )

    role_outputs: list[dict[str, Any]] = []
    verify_ok: bool | None = None
    verify_log = ""

    for role_name in ROLE_ORDER:
        spec = ROLE_SPECS[role_name]
        output = run_role(role=spec, trigger=trigger, meeting_id=meeting_id, prior_outputs=role_outputs, contract=contract)
        role_outputs.append(output)
        post_message(
            username=role_name,
            content=format_role_message(output, meeting_id, trigger),
            meeting_id=meeting_id,
            phase=role_name,
            trigger_id=trigger["id"],
            thread_id=trigger.get("thread_id"),
        )
        if role_name != "executor" and output.get("needs_human"):
            emit_console(role_name, "needs_human=true -> stop chain")
            break
        if role_name == "executor":
            if output.get("needs_human") or output.get("status") in {"blocked", "fail"}:
                verify_ok = None
                verify_log = "executor reported blocked/needs_human; verify gate skipped"
                emit_console("verify", "skipped because executor reported blocked/needs_human")
            else:
                verify_ok, verify_log = run_verify_gate()

    next_action = compute_next_action(role_outputs, contract)
    post_message(
        username="scribe",
        content=textwrap.dedent(
            f"""
            [meeting:{meeting_id}] ??
            ?? ??:
            {chr(10).join(f"- {item['role']}: {item['summary']}" for item in role_outputs) or '- ?? ?? ??'}
            ?? ??: {next_action}
            """
        ).strip(),
        meeting_id=meeting_id,
        phase="meeting_end",
        trigger_id=trigger["id"],
        thread_id=trigger.get("thread_id"),
    )
    emit_console("meeting", f"end id={meeting_id} roles={len(role_outputs)} next={trim(next_action, 120)}")
    return role_outputs, verify_ok, verify_log, meeting_id


def mark_trigger_done(loop_state: dict[str, Any], trigger: dict[str, Any]) -> None:
    if trigger["kind"] == "discord_user":
        loop_state.setdefault("handled_discord_message_ids", []).append(trigger["message_id"])
    if trigger["kind"] == "followup":
        loop_state["pending_followup"] = {}
    loop_state["last_autonomous_cycle_at"] = iso_now()


def maybe_report_repeated_failure(loop_state: dict[str, Any], trigger: dict[str, Any]) -> None:
    streak = int(loop_state.get("failure_streak", 0))
    if streak < 3:
        return
    post_message(
        username="watchdog",
        content=f"[meeting:{loop_state.get('last_meeting_id', '')}] 같은 실패가 {streak}회 반복됐다. 같은 방법 반복을 중지하고 우회책을 먼저 고른다.",
        meeting_id=loop_state.get("last_meeting_id", "watchdog"),
        phase="failure_streak",
        trigger_id=trigger["id"],
        thread_id=trigger.get("thread_id"),
    )


def write_idle_journal(iteration: int, loop_state: dict[str, Any], contract: AgentsContract) -> None:
    write_iteration_journal(
        iteration=iteration,
        meeting_id=loop_state.get("last_meeting_id", f"idle-{iteration:04d}"),
        trigger=None,
        role_outputs=[],
        verify_ok=None,
        verify_log="",
        next_action=contract.primary_task or "Discord ?? ?? ?? P0 ?? ??",
        note="??? ? Discord ??? ?? ?? ?? ??? ?? ??? ??",
    )


def main() -> int:
    ensure_dirs()
    contract = parse_agents_contract()
    sync_discord_replies()
    loop_state = load_loop_state()
    iteration = int(os.getenv("OMX_LOOP_ITERATION", "0") or "0")
    if iteration <= 0:
        iteration = int(loop_state.get("iteration", 0)) + 1
    loop_state["iteration"] = iteration
    emit_console("loop", f"iteration={iteration} workspace={OMX_WORKSPACE_ROOT}")

    trigger = select_trigger(loop_state, contract)
    if not trigger:
        emit_console("idle", "no trigger")
        write_idle_journal(iteration, loop_state, contract)
        write_runtime_status(status="idle", detail="no trigger", trigger="idle")
        save_loop_state(loop_state)
        return 0

    note = "Discord ?? ?? ??" if trigger["kind"] == "discord_user" else "?? ?? ??"
    emit_console("trigger", f"kind={trigger['kind']} label={trim(trigger['label'], 140)}")
    try:
        role_outputs, verify_ok, verify_log, meeting_id = run_meeting(loop_state, trigger, contract)
        next_action = compute_next_action(role_outputs, contract)
        if verify_ok is not None:
            update_failure_streak(loop_state, verify_ok, trigger)
            if not verify_ok:
                maybe_report_repeated_failure(loop_state, trigger)
        mark_trigger_done(loop_state, trigger)
        schedule_followup(loop_state, role_outputs, next_action, meeting_id)
        write_iteration_journal(
            iteration=iteration,
            meeting_id=meeting_id,
            trigger=trigger,
            role_outputs=role_outputs,
            verify_ok=verify_ok,
            verify_log=verify_log,
            next_action=next_action,
            note=note,
        )
        loop_state["last_result"] = role_outputs[-1]["status"] if role_outputs else "idle"
        save_loop_state(loop_state)
        write_runtime_status(status="completed", detail=trim(next_action, 160), meeting_id=meeting_id, role="scribe", trigger=trigger["kind"])
        emit_console("loop", f"iteration={iteration} completed result={loop_state['last_result']}")
        return 0
    except Exception as exc:
        failure_note = trim(str(exc), 1500)
        emit_console("error", failure_note)
        write_verify_failure(
            status="active",
            failing_command="scripts/omx_autonomous_loop.py",
            symptom="meeting execution failed",
            likely_cause=failure_note,
            next_fix="inspect the latest role log and rerun the smallest failing step first",
        )
        write_iteration_journal(
            iteration=iteration,
            meeting_id=loop_state.get("last_meeting_id", f"failed-{iteration:04d}"),
            trigger=trigger,
            role_outputs=[],
            verify_ok=False,
            verify_log=failure_note,
            next_action="???/omx exec ??? ?? ?? ?? ??",
            note="?? ?? ? ?? ??",
        )
        loop_state["last_result"] = "failed"
        update_failure_streak(loop_state, False, trigger)
        maybe_report_repeated_failure(loop_state, trigger)
        if trigger["kind"] in {"discord_user", "followup"} and int(loop_state.get("failure_streak", 0)) >= 3:
            mark_trigger_done(loop_state, trigger)
        save_loop_state(loop_state)
        write_runtime_status(status="failed", detail=failure_note, meeting_id=loop_state.get("last_meeting_id", ""), role="watchdog", trigger=trigger["kind"])
        post_message(
            username="watchdog",
            content=f"[meeting:{loop_state.get('last_meeting_id', '')}] ?? ??: {failure_note}",
            meeting_id=loop_state.get("last_meeting_id", f"failed-{iteration:04d}"),
            phase="loop_error",
            trigger_id=trigger["id"],
            thread_id=trigger.get("thread_id"),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
