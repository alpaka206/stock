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

TASK_FILE = STATE_DIR / "TASK.md"
STATE_FILE = STATE_DIR / "STATE.md"
BACKLOG_FILE = STATE_DIR / "BACKLOG.md"
NEXT_PROMPT_FILE = STATE_DIR / "NEXT_PROMPT.md"
DISCORD_STATUS_FILE = STATE_DIR / "DISCORD_STATUS.md"
VERIFY_FAILURE_FILE = STATE_DIR / "VERIFY_LAST_FAILURE.md"
DISCORD_IMPORTANT_FILE = STATE_DIR / "DISCORD_IMPORTANT.md"
DISCORD_INBOX_LOG = STATE_DIR / "DISCORD_INBOX.jsonl"
TEAM_CONVERSATION_LOG = STATE_DIR / "TEAM_CONVERSATION.jsonl"
LOOP_STATE_FILE = STATE_DIR / "OMX_LOOP_STATE.json"
LOOP_RUNTIME_STATUS_FILE = RUNTIME_DIR / "omx-loop-status.json"
ROLE_SCHEMA_FILE = ROOT / "scripts" / "omx_role_output.schema.json"

DISCORD_BRIDGE_PORT = int(os.getenv("DISCORD_BRIDGE_PORT", "8787"))
AUTONOMOUS_IDLE_INTERVAL_SECONDS = max(int(os.getenv("OMX_AUTONOMOUS_IDLE_INTERVAL_SECONDS", "300")), 60)
ROLE_TIMEOUT_SECONDS = max(int(os.getenv("OMX_ROLE_TIMEOUT_SECONDS", "900")), 120)
VERIFY_TIMEOUT_SECONDS = max(int(os.getenv("OMX_VERIFY_TIMEOUT_SECONDS", "1800")), 120)
RECENT_CONVERSATION_LIMIT = max(int(os.getenv("OMX_RECENT_CONVERSATION_LIMIT", "12")), 4)
MAX_TRACKED_IDS = 400
ROLE_ORDER = ("planner", "critic", "researcher", "architect", "executor")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
RAW_UNICODE_ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")
DOUBLE_QUESTION_RE = re.compile(r"\?\?")
HANGUL_RE = re.compile(r"[가-힣]")


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
    "planner": RoleSpec("planner", "최신 트리거와 상태를 읽고 이번 iteration의 가장 작은 P0를 고른다.", "read-only"),
    "critic": RoleSpec("critic", "계획의 허점, 정책 위반, 검증 누락, 재발 위험을 먼저 잡는다.", "read-only"),
    "researcher": RoleSpec("researcher", "관련 파일, 상태, 테스트, 데이터 경로를 짚어 실행 전 사실관계를 보강한다.", "read-only"),
    "architect": RoleSpec("architect", "작업을 되돌리기 쉬운 구현 단위와 검증 단위로 정리한다.", "read-only"),
    "executor": RoleSpec("executor", "합의한 최소 작업을 즉시 실행 가능한 액션으로 정리하고 다음 구현 단계를 확정한다.", "read-only"),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def trim(text: str, limit: int = 3000) -> str:
    normalized = re.sub(r"\s+\n", "\n", text).strip()
    return normalized if len(normalized) <= limit else normalized[: limit - 3].rstrip() + "..."


def sanitize_text(value: str) -> str:
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = CONTROL_CHAR_RE.sub("", text).strip()
    question_count = text.count("?")
    if question_count >= 3 and not HANGUL_RE.search(text):
        ascii_letters = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        if ascii_letters < 8:
            return "[인코딩 손상으로 원문을 보존하지 못함]"
    text = DOUBLE_QUESTION_RE.sub("물음표 두 개", text)
    text = RAW_UNICODE_ESCAPE_RE.sub("[유니코드 이스케이프 제거]", text)
    return text


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): sanitize_value(item) for key, item in value.items()}
    return value


def slugify(value: str) -> str:
    lowered = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value.lower())
    return re.sub(r"-{2,}", "-", lowered).strip("-") or "task"


def read_text(path: Path, default: str = "") -> str:
    return default if not path.exists() else path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(sanitize_value(payload), ensure_ascii=False, indent=2) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(sanitize_value(payload), ensure_ascii=False) + "\n")


def rewrite_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(sanitize_value(item), ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for raw in read_text(path).splitlines():
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


def repair_state_logs() -> None:
    for path in (DISCORD_INBOX_LOG, TEAM_CONVERSATION_LOG):
        if not path.exists():
            continue
        repaired = [sanitize_value(item) for item in load_jsonl(path)]
        rewrite_jsonl(path, repaired)


def emit_console(phase: str, message: str) -> None:
    print(f"[omx][{iso_now()}][{phase}] {message}", flush=True)


def ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)


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
        if ctypes.windll.kernel32.GetShortPathNameW(raw_root, buffer, len(buffer)):
            return buffer.value or raw_root
    except Exception:
        pass
    return raw_root


OMX_WORKSPACE_ROOT = resolve_workspace_root()


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

    docs: list[str] = []
    collecting = False
    for line in text.splitlines():
        stripped = line.strip()
        if not collecting and stripped == "먼저 읽을 문서":
            collecting = True
            continue
        if collecting and stripped.startswith("## "):
            break
        if collecting and stripped.startswith("- "):
            docs.append(stripped[2:].strip().strip("`"))
        elif collecting and docs and stripped:
            break

    return AgentsContract(
        primary_task=find_value("PRIMARY_TASK"),
        min_exit_condition=find_value("MIN_EXIT_CONDITION"),
        auto_continue_policy=find_value("AUTO_CONTINUE_POLICY"),
        release_to_main_policy=find_value("RELEASE_TO_MAIN_POLICY"),
        required_docs=tuple(docs),
        consensus_order=find_value("MULTI_AGENT_CONSENSUS", "planner -> critic -> researcher -> architect -> executor -> verifier"),
    )


def parse_backlog_first_unchecked(text: str) -> str:
    current_section = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
        elif current_section == "P0" and stripped.startswith("- [ ] "):
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
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


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
    merged = default | payload if isinstance(payload, dict) else default
    if not isinstance(merged.get("handled_discord_message_ids"), list):
        merged["handled_discord_message_ids"] = []
    if not isinstance(merged.get("pending_followup"), dict):
        merged["pending_followup"] = {}
    return merged


def save_loop_state(payload: dict[str, Any]) -> None:
    handled = payload.get("handled_discord_message_ids", [])
    if isinstance(handled, list):
        payload["handled_discord_message_ids"] = handled[-MAX_TRACKED_IDS:]
    write_json(LOOP_STATE_FILE, payload)


def update_important_discord_notes() -> None:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in reversed(load_jsonl(DISCORD_INBOX_LOG)):
        if str(item.get("source")) != "discord_user":
            continue
        message_id = str(item.get("message_id", "")).strip()
        content = str(item.get("content", "")).strip()
        if not message_id or not content or message_id in seen:
            continue
        seen.add(message_id)
        entries.append(item)

    latest = entries[0] if entries else None
    superseded = entries[1:]

    lines = [
        "# 중요한 Discord 지시",
        "",
        "- 최신 사용자 지시 1건만 회의 트리거로 사용한다.",
        "- 과거 미처리 지시는 superseded로 정리하고 다시 읽지 않는다.",
    ]
    if latest:
        lines.extend(
            [
                "",
                "## 최신 지시",
                "",
                f"- {latest.get('created_at', '')} / `{latest.get('message_id', '')}` / {latest.get('author', 'unknown')}",
                f"- 사용자 지시: {latest.get('content', '')}",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## 최신 지시",
                "",
                "- 현재 대기 중인 Discord 사용자 지시가 없다.",
            ]
        )
    if superseded:
        lines.extend(
            [
                "",
                "## Superseded",
                "",
                f"- 최신 지시 도착으로 이전 지시 {len(superseded)}건은 다시 읽지 않는다.",
            ]
        )
    write_text(DISCORD_IMPORTANT_FILE, "\n".join(lines) + "\n")


def select_trigger(loop_state: dict[str, Any], contract: AgentsContract) -> dict[str, Any] | None:
    handled = {str(item) for item in loop_state.get("handled_discord_message_ids", [])}
    pending = [
        item
        for item in load_jsonl(DISCORD_INBOX_LOG)
        if str(item.get("message_id", "")).strip()
        and str(item.get("content", "")).strip()
        and str(item.get("message_id")) not in handled
    ]
    if pending:
        latest = pending[-1]
        return {
            "id": f"discord-{latest['message_id']}",
            "kind": "discord_user",
            "message_id": str(latest.get("message_id", "")).strip(),
            "author": str(latest.get("author", "unknown")).strip(),
            "content": str(latest.get("content", "")).strip(),
            "thread_id": str(latest.get("thread_id", "")).strip() or None,
            "superseded_message_ids": [
                str(item.get("message_id", "")).strip()
                for item in pending[:-1]
                if str(item.get("message_id", "")).strip()
            ],
            "label": f"Discord 사용자 지시: {str(latest.get('content', '')).strip()}",
        }

    failure = parse_verify_failure(read_text(VERIFY_FAILURE_FILE))
    if failure.get("status") == "active":
        cmd = failure.get("failing_command", "unknown")
        return {
            "id": f"verify-{slugify(cmd)}",
            "kind": "verify_failure",
            "content": cmd,
            "thread_id": None,
            "label": f"검증 실패: {cmd}",
        }

    followup = str((loop_state.get("pending_followup") or {}).get("content", "")).strip()
    if followup:
        return {
            "id": f"followup-{slugify(followup)}",
            "kind": "followup",
            "content": followup,
            "thread_id": None,
            "label": f"후속 액션: {followup}",
        }

    last_cycle_raw = str(loop_state.get("last_autonomous_cycle_at", "")).strip()
    try:
        last_cycle = (
            datetime.fromisoformat(last_cycle_raw.replace("Z", "+00:00"))
            if last_cycle_raw
            else utc_now() - timedelta(seconds=AUTONOMOUS_IDLE_INTERVAL_SECONDS + 1)
        )
    except ValueError:
        last_cycle = utc_now() - timedelta(seconds=AUTONOMOUS_IDLE_INTERVAL_SECONDS + 1)
    if (utc_now() - last_cycle).total_seconds() < AUTONOMOUS_IDLE_INTERVAL_SECONDS:
        return None

    backlog = parse_backlog_first_unchecked(read_text(BACKLOG_FILE))
    if backlog:
        return {
            "id": f"autonomous-{slugify(backlog)}",
            "kind": "autonomous_backlog",
            "content": backlog,
            "thread_id": None,
            "label": f"자율 백로그: {backlog}",
        }

    next_prompt = parse_next_prompt_action(read_text(NEXT_PROMPT_FILE))
    if next_prompt:
        return {
            "id": f"next-{slugify(next_prompt)}",
            "kind": "next_prompt",
            "content": next_prompt,
            "thread_id": None,
            "label": f"다음 프롬프트: {next_prompt}",
        }

    if contract.primary_task:
        return {
            "id": "agents-primary-task",
            "kind": "agents_primary_task",
            "content": contract.primary_task,
            "thread_id": None,
            "label": "최상위 계약: PRIMARY_TASK",
        }
    return None


def bridge_url(path: str) -> str:
    return f"http://127.0.0.1:{DISCORD_BRIDGE_PORT}{path}"


def sync_discord_replies() -> None:
    try:
        req = request.Request(bridge_url("/sync-replies"), data=b"{}", method="POST")
        with request.urlopen(req, timeout=15):
            return
    except Exception:
        return


def load_discord_env_values() -> dict[str, str]:
    env_path = Path(os.getenv("DISCORD_ENV_FILE", str(ROOT / "omx_discord_bridge" / ".env.discord")))
    values: dict[str, str] = {}
    for line in read_text(env_path).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def append_local_conversation(
    username: str,
    content: str,
    source: str,
    meeting_id: str,
    phase: str,
    trigger_id: str,
    thread_id: str | None,
) -> None:
    username = sanitize_text(username)
    content = sanitize_text(content)
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


def direct_discord_webhook_post(webhook_url: str, content: str, username: str, thread_id: str | None) -> bool:
    if not webhook_url:
        return False
    username = sanitize_text(username)
    content = sanitize_text(content)
    target = webhook_url if not thread_id else f"{webhook_url}{'&' if '?' in webhook_url else '?'}{parse.urlencode({'thread_id': thread_id})}"
    payload = json.dumps(
        {"content": content, "username": username, "allowed_mentions": {"parse": []}}
    ).encode("utf-8")
    req = request.Request(target, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=15) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def post_message(
    username: str,
    content: str,
    meeting_id: str,
    phase: str,
    trigger_id: str,
    thread_id: str | None,
    source: str = "agent",
) -> None:
    username = sanitize_text(username)
    content = sanitize_text(content)
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
        req = request.Request(
            bridge_url("/event"),
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=15) as response:
            if 200 <= response.status < 300:
                return
    except error.URLError:
        pass
    except Exception:
        pass

    env_values = load_discord_env_values()
    sent = direct_discord_webhook_post(
        env_values.get("DISCORD_WEBHOOK_URL", "").strip(),
        content,
        username,
        thread_id,
    )
    append_local_conversation(
        username,
        content,
        source if sent else f"{source}_local",
        meeting_id,
        phase,
        trigger_id,
        thread_id,
    )


def find_omx_exec() -> str:
    candidates = (
        os.getenv("OMX_EXECUTABLE", "").strip(),
        which("omx") or "",
        which("omx.cmd") or "",
        str(Path.home() / "AppData" / "Roaming" / "npm" / "omx.cmd"),
    )
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError("omx executable not found")


def find_bash() -> str:
    candidates = (
        os.getenv("OMX_BASH", "").strip(),
        r"C:\Program Files\Git\bin\bash.exe",
        which("bash.exe") or "",
        which("bash") or "",
    )
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError("bash executable not found")


def build_context_excerpt() -> str:
    items = [
        ("DISCORD_IMPORTANT.md", DISCORD_IMPORTANT_FILE, 1000),
        ("TASK.md", TASK_FILE, 1200),
        ("STATE.md", STATE_FILE, 1000),
        ("BACKLOG.md", BACKLOG_FILE, 1000),
        ("NEXT_PROMPT.md", NEXT_PROMPT_FILE, 900),
        ("VERIFY_LAST_FAILURE.md", VERIFY_FAILURE_FILE, 700),
        ("DISCORD_STATUS.md", DISCORD_STATUS_FILE, 900),
    ]
    return "\n\n".join(f"## {label}\n{trim(read_text(path), limit)}" for label, path, limit in items)


def build_recent_excerpt() -> str:
    recent = load_jsonl(TEAM_CONVERSATION_LOG)[-RECENT_CONVERSATION_LIMIT:]
    if not recent:
        return "- 최근 대화 없음"
    return "\n".join(
        f"- {item.get('role') or item.get('author') or item.get('source')}: {trim(str(item.get('content', '')), 180)}"
        for item in recent
    )


def build_role_prompt(
    role: RoleSpec,
    trigger: dict[str, Any],
    meeting_id: str,
    prior_outputs: list[dict[str, Any]],
    contract: AgentsContract,
) -> str:
    prior = "\n".join(
        textwrap.dedent(
            f"""\
            ### {item['role']}
            - status: {item['status']}
            - summary: {item['summary']}
            - rationale: {item['rationale']}
            - proposed_action: {item['proposed_action']}
            """
        ).strip()
        for item in prior_outputs
    ) or "- 없음"
    docs = "\n".join(f"- {item}" for item in contract.required_docs) or "- 없음"
    return textwrap.dedent(
        f"""\
        당신은 OMX 역할 `{role.name}`이다.
        목표: {role.goal}

        현재 회의
        - meeting_id: {meeting_id}
        - trigger_kind: {trigger['kind']}
        - trigger_label: {trigger['label']}
        - trigger_content: {trigger.get('content', '')}
        - superseded_message_ids: {', '.join(trigger.get('superseded_message_ids', [])) or '없음'}

        최상위 계약
        - PRIMARY_TASK: {contract.primary_task}
        - MIN_EXIT_CONDITION: {contract.min_exit_condition}
        - AUTO_CONTINUE_POLICY: {contract.auto_continue_policy}
        - RELEASE_TO_MAIN_POLICY: {contract.release_to_main_policy}
        - MULTI_AGENT_CONSENSUS: {contract.consensus_order}

        규칙
        - 최신 Discord 사용자 지시 1건만 우선한다.
        - superseded_message_ids는 다시 읽지 않는다.
        - 질문은 정말 막힌 경우에만 최소화한다.
        - `??` 같은 플레이스홀더나 raw unicode escape를 쓰지 않는다.
        - 비밀, 토큰, webhook URL, env 값은 출력하지 않는다.
        - 출처 없는 가격, 뉴스, 점수를 만들지 않는다.
        - 응답은 JSON schema를 만족해야 하며 핵심 문장은 한국어로 쓴다.
        - read-only 역할은 changed_files를 비운다.
        - needs_human은 외부 권한이나 비밀 부족 때문에 지금 진행할 수 없을 때만 true다.

        필수 참고 문서
        {docs}

        상태 요약
        {build_context_excerpt()}

        최근 대화
        {build_recent_excerpt()}

        이전 역할 출력
        {prior}
        """
    ).strip()


def normalize_role_output(role: RoleSpec, payload: dict[str, Any]) -> dict[str, Any]:
    payload = sanitize_value(payload)
    payload["role"] = role.name
    for key in ("risks", "verification", "changed_files", "followups"):
        if not isinstance(payload.get(key), list):
            payload[key] = []
    if not role.writable:
        payload["changed_files"] = []
    for key in ("summary", "rationale", "proposed_action", "status"):
        payload[key] = str(payload.get(key, "")).strip()
    if not payload["status"]:
        payload["status"] = "continue"
    try:
        payload["confidence"] = float(payload.get("confidence", 0))
    except Exception:
        payload["confidence"] = 0.0
    payload["needs_human"] = bool(payload.get("needs_human", False))
    return payload


def run_role(
    role: RoleSpec,
    trigger: dict[str, Any],
    meeting_id: str,
    prior_outputs: list[dict[str, Any]],
    contract: AgentsContract,
) -> dict[str, Any]:
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

    prompt = build_role_prompt(role, trigger, meeting_id, prior_outputs, contract)
    emit_console(role.name, f"run start trigger={trim(trigger['label'], 100)}")
    with log_file.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            args,
            input=prompt.encode("utf-8"),
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
            timeout=ROLE_TIMEOUT_SECONDS,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"{role.name} failed with exit={completed.returncode}: {trim(read_text(log_file), 1200)}")
    payload = load_json(output_file, {})
    if not isinstance(payload, dict):
        raise RuntimeError(f"{role.name} returned non-object payload")
    normalized = normalize_role_output(role, payload)
    emit_console(role.name, f"done status={normalized['status']} next={trim(normalized['proposed_action'], 100)}")
    return normalized


def format_role_message(payload: dict[str, Any], meeting_id: str, trigger: dict[str, Any]) -> str:
    def render(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- 없음"

    return textwrap.dedent(
        f"""\
        [meeting:{meeting_id}][{payload['role']}]
        트리거: {trigger['label']}
        상태: {payload['status']}
        판단: {payload['summary']}
        근거: {payload['rationale']}
        다음 액션: {payload['proposed_action']}
        리스크:
        {render(payload['risks'])}
        검증:
        {render(payload['verification'])}
        변경 파일:
        {render(payload['changed_files'])}
        후속:
        {render(payload['followups'])}
        confidence: {payload['confidence']:.2f}
        """
    ).strip()


def run_bash_script(script_path: Path, log_name: str, timeout: int) -> tuple[int, str]:
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


def write_verify_failure(status: str, failing_command: str, symptom: str, likely_cause: str, next_fix: str) -> None:
    write_text(
        VERIFY_FAILURE_FILE,
        textwrap.dedent(
            f"""\
            # 최근 검증 실패

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
        try:
            returncode, log_text = run_bash_script(script_path, log_name, timeout)
        except Exception as exc:
            write_verify_failure("active", label, "verification setup failed", str(exc), "bash 경로와 스크립트 실행 환경을 먼저 복구한다.")
            return False, f"$ {label}\n{exc}"
        logs.append(f"$ {label}\n{log_text}")
        if returncode != 0:
            write_verify_failure("active", label, "verification command returned non-zero", f"inspect .omx/runtime/{log_name}", "실패한 명령을 먼저 통과시키고 같은 명령부터 다시 실행한다.")
            return False, "\n\n".join(logs)
    write_verify_failure("clear", "", "", "", "")
    return True, "\n\n".join(logs)


def build_verifier_output(executor_output: dict[str, Any] | None, verify_ok: bool | None, verify_log: str) -> dict[str, Any]:
    if executor_output is None:
        return {
            "role": "verifier",
            "status": "blocked",
            "summary": "executor 전에 회의가 중단되어 검증 단계에 진입하지 못했다.",
            "rationale": "executor 결과가 없다.",
            "proposed_action": "막힌 역할의 사유를 먼저 해소한다.",
            "risks": ["구현 상태를 검증하지 못했다."],
            "verification": ["verify gate skipped"],
            "changed_files": [],
            "followups": ["막힌 역할 원인 해소"],
            "confidence": 0.2,
            "needs_human": False,
        }
    if executor_output.get("needs_human") or executor_output.get("status") in {"blocked", "fail"}:
        return {
            "role": "verifier",
            "status": "blocked",
            "summary": "executor가 차단 상태라 guard/verify gate를 생략했다.",
            "rationale": executor_output.get("summary", "executor blocked"),
            "proposed_action": "executor 차단 원인을 해결하고 같은 작업을 다시 검증한다.",
            "risks": ["구현 결과가 검증되지 않았다."],
            "verification": ["executor blocked; verify gate skipped"],
            "changed_files": [],
            "followups": ["executor 차단 원인 해결"],
            "confidence": 0.35,
            "needs_human": bool(executor_output.get("needs_human", False)),
        }
    if verify_ok is None:
        return {
            "role": "verifier",
            "status": "done",
            "summary": "회의형 executor가 실행 계획까지만 정리했고 실제 코드 변경은 아직 수행하지 않았다.",
            "rationale": trim(verify_log, 400) or "회의 단계라 guard/verify를 생략했다.",
            "proposed_action": "다음 구현 iteration에서 executor 액션을 실제 코드 변경과 검증으로 이어간다.",
            "risks": ["실제 코드 변경 전이라 기능 상태는 아직 바뀌지 않았을 수 있다."],
            "verification": ["meeting-only executor; verify gate skipped"],
            "changed_files": [],
            "followups": list(executor_output.get("followups", [])) or ["executor 액션을 실제 구현으로 이어간다."],
            "confidence": 0.62,
            "needs_human": False,
        }
    if verify_ok:
        return {
            "role": "verifier",
            "status": "pass",
            "summary": "executor 이후 guard/verify gate를 통과했다.",
            "rationale": "scripts/no_secrets_guard.sh와 scripts/verify_minimal.sh가 모두 성공했다.",
            "proposed_action": "다음 가장 작은 후속 구현 또는 QA 범위로 진행한다.",
            "risks": [],
            "verification": ["scripts/no_secrets_guard.sh: pass", "scripts/verify_minimal.sh: pass"],
            "changed_files": [],
            "followups": list(executor_output.get("followups", [])),
            "confidence": 0.86,
            "needs_human": False,
        }
    return {
        "role": "verifier",
        "status": "fail",
        "summary": "executor 이후 guard/verify gate에서 실패가 발생했다.",
        "rationale": trim(verify_log, 400),
        "proposed_action": "VERIFY_LAST_FAILURE.md에 적힌 실패 명령부터 복구한다.",
        "risks": ["실패한 검증을 무시하면 회귀나 비밀 문제가 남을 수 있다."],
        "verification": ["guard/verify gate failed"],
        "changed_files": [],
        "followups": ["실패한 검증 명령 복구"],
        "confidence": 0.28,
        "needs_human": False,
    }


def compute_next_action(role_outputs: list[dict[str, Any]], contract: AgentsContract) -> str:
    for output in reversed(role_outputs):
        for candidate in list(output.get("followups", [])) + [output.get("proposed_action", "")]:
            candidate = str(candidate).strip()
            if candidate:
                return candidate
    return contract.primary_task or "최상위 계약의 다음 P0를 다시 고른다."


def schedule_followup(loop_state: dict[str, Any], role_outputs: list[dict[str, Any]], next_action: str, meeting_id: str) -> None:
    loop_state["last_next_action"] = next_action.strip()
    if not role_outputs or role_outputs[-1].get("needs_human") or not next_action.strip():
        loop_state["pending_followup"] = {}
        return
    loop_state["pending_followup"] = {"content": next_action.strip(), "source_meeting_id": meeting_id, "created_at": iso_now()}


def write_iteration_journal(iteration: int, meeting_id: str, trigger: dict[str, Any] | None, role_outputs: list[dict[str, Any]], verify_ok: bool | None, verify_log: str, next_action: str, note: str) -> None:
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
        for item in ("scripts/no_secrets_guard.sh: pass", "scripts/verify_minimal.sh: pass"):
            if item not in verification_lines:
                verification_lines.append(item)
    journal = textwrap.dedent(
        f"""\
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


def maybe_report_repeated_failure(loop_state: dict[str, Any], trigger: dict[str, Any]) -> None:
    streak = int(loop_state.get("failure_streak", 0))
    if streak < 3:
        return
    post_message("watchdog", f"[meeting:{loop_state.get('last_meeting_id', '')}] 같은 실패가 {streak}회 반복되었다. 같은 방법 반복을 중단하고 우회책을 먼저 고른다.", loop_state.get("last_meeting_id", "watchdog"), "failure_streak", trigger["id"], trigger.get("thread_id"))


def mark_trigger_done(loop_state: dict[str, Any], trigger: dict[str, Any]) -> None:
    if trigger["kind"] == "discord_user":
        handled = loop_state.setdefault("handled_discord_message_ids", [])
        handled.extend(trigger.get("superseded_message_ids", []))
        handled.append(trigger["message_id"])
    if trigger["kind"] == "followup":
        loop_state["pending_followup"] = {}
    loop_state["last_autonomous_cycle_at"] = iso_now()


def run_meeting(loop_state: dict[str, Any], trigger: dict[str, Any], contract: AgentsContract) -> tuple[list[dict[str, Any]], bool | None, str, str]:
    loop_state["meeting_counter"] = int(loop_state.get("meeting_counter", 0)) + 1
    meeting_id = f"{utc_now().strftime('%Y%m%d-%H%M%S')}-{loop_state['meeting_counter']:04d}"
    loop_state["last_meeting_id"] = meeting_id
    if trigger["kind"] == "discord_user":
        update_important_discord_notes()

    emit_console("meeting", f"start id={meeting_id} trigger={trim(trigger['label'], 120)}")
    post_message("coordinator", f"[meeting:{meeting_id}] 회의를 시작한다. trigger={trigger['label']}", meeting_id, "meeting_start", trigger["id"], trigger.get("thread_id"))

    role_outputs: list[dict[str, Any]] = []
    executor_output: dict[str, Any] | None = None
    verify_ok: bool | None = None
    verify_log = ""
    for role_name in ROLE_ORDER:
        output = run_role(ROLE_SPECS[role_name], trigger, meeting_id, role_outputs, contract)
        role_outputs.append(output)
        post_message(role_name, format_role_message(output, meeting_id, trigger), meeting_id, role_name, trigger["id"], trigger.get("thread_id"))
        if role_name != "executor" and output.get("needs_human"):
            break
        if role_name == "executor":
            executor_output = output
            if output.get("needs_human") or output.get("status") in {"blocked", "fail"}:
                verify_log = "executor가 차단 상태라 verify gate를 생략했다."
            elif ROLE_SPECS[role_name].writable:
                verify_ok, verify_log = run_verify_gate()
            else:
                verify_log = "회의형 executor는 실행 계획만 정리하므로 guard/verify를 생략했다."
            break

    verifier_output = build_verifier_output(executor_output, verify_ok, verify_log)
    role_outputs.append(verifier_output)
    post_message("verifier", format_role_message(verifier_output, meeting_id, trigger), meeting_id, "verifier", trigger["id"], trigger.get("thread_id"))

    next_action = compute_next_action(role_outputs, contract)
    post_message(
        "scribe",
        textwrap.dedent(
            f"""\
            [meeting:{meeting_id}] 회의 종료
            역할 요약:
            {chr(10).join(f"- {item['role']}: {item['summary']}" for item in role_outputs) or '- 없음'}
            다음 액션: {next_action}
            """
        ).strip(),
        meeting_id,
        "meeting_end",
        trigger["id"],
        trigger.get("thread_id"),
    )
    emit_console("meeting", f"end id={meeting_id} roles={len(role_outputs)} next={trim(next_action, 120)}")
    return role_outputs, verify_ok, verify_log, meeting_id


def write_idle_journal(iteration: int, loop_state: dict[str, Any], contract: AgentsContract) -> None:
    write_iteration_journal(iteration, loop_state.get("last_meeting_id", f"idle-{iteration:04d}"), None, [], None, "", contract.primary_task or "Discord 최신 지시를 기다린다.", "새 트리거가 없어 대기한다.")


def main() -> int:
    ensure_dirs()
    repair_state_logs()
    contract = parse_agents_contract()
    sync_discord_replies()
    loop_state = load_loop_state()
    iteration = int(os.getenv("OMX_LOOP_ITERATION", "0") or "0") or int(loop_state.get("iteration", 0)) + 1
    loop_state["iteration"] = iteration
    write_runtime_status(status="running", detail=f"iteration={iteration}", trigger="loop")
    emit_console("loop", f"iteration={iteration} workspace={OMX_WORKSPACE_ROOT}")

    trigger = select_trigger(loop_state, contract)
    if not trigger:
        emit_console("idle", "no trigger")
        write_idle_journal(iteration, loop_state, contract)
        write_runtime_status(status="idle", detail="no trigger", trigger="idle")
        save_loop_state(loop_state)
        return 0

    note = "Discord 최신 사용자 지시 처리" if trigger["kind"] == "discord_user" else "자율 또는 복구 작업 처리"
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
        write_iteration_journal(iteration, meeting_id, trigger, role_outputs, verify_ok, verify_log, next_action, note)
        loop_state["last_result"] = role_outputs[-1]["status"] if role_outputs else "idle"
        save_loop_state(loop_state)
        write_runtime_status(status="completed", detail=trim(next_action, 160), meeting_id=meeting_id, role="scribe", trigger=trigger["kind"])
        emit_console("loop", f"iteration={iteration} completed result={loop_state['last_result']}")
        return 0
    except Exception as exc:
        failure_note = trim(str(exc), 1500)
        emit_console("error", failure_note)
        write_verify_failure("active", "scripts/omx_autonomous_loop.py", "meeting execution failed", failure_note, "최신 role log를 확인하고 가장 작은 실패 단계부터 다시 실행한다.")
        write_iteration_journal(iteration, loop_state.get("last_meeting_id", f"failed-{iteration:04d}"), trigger, [], False, failure_note, "OMX role 실행 오류를 먼저 복구한다.", "회의 실행 중 예외가 발생했다.")
        loop_state["last_result"] = "failed"
        update_failure_streak(loop_state, False, trigger)
        maybe_report_repeated_failure(loop_state, trigger)
        if trigger["kind"] in {"discord_user", "followup"} and int(loop_state.get("failure_streak", 0)) >= 3:
            mark_trigger_done(loop_state, trigger)
        save_loop_state(loop_state)
        write_runtime_status(status="failed", detail=failure_note, meeting_id=loop_state.get("last_meeting_id", ""), role="watchdog", trigger=trigger["kind"])
        post_message("watchdog", f"[meeting:{loop_state.get('last_meeting_id', '')}] 회의 실행 실패: {failure_note}", loop_state.get("last_meeting_id", f"failed-{iteration:04d}"), "loop_error", trigger["id"], trigger.get("thread_id"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
