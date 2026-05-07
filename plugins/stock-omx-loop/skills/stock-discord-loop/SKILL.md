---
name: stock-discord-loop
description: Operate and repair the stock repo's Discord-driven OMX loop, user-to-agent relay, and agent-to-agent meeting flow. Use when Codex needs to run or debug `scripts/omx_autonomous_loop.py`, `omx_discord_bridge/discord_omx_bridge.py`, `.omx/state` files, Windows launch scripts, or the repo-local Codex workspace/plugin setup for this repository.
---

# Stock Discord Loop

## Overview

이 스킬은 이 저장소에 이미 들어 있는 OMX 자동화와 Discord 브리지를 Codex가 안전하게 읽고, 실행하고, 점검하고, 줄여서 운용하도록 돕는다.

핵심 경로:
- `../../../AGENTS.md`
- `../../../docs/discord-bridge.md`
- `../../../scripts/omx_autonomous_loop.py`
- `../../../scripts/run-discord-bridge.ps1`
- `../../../scripts/omx-loop.ps1`
- `../../../omx_discord_bridge/discord_omx_bridge.py`
- `../../../.omx/state/`

## Quick Start

1. 먼저 `../../../AGENTS.md`, `../../../docs/discord-bridge.md`, `../../../.omx/state/TASK.md`, `../../../.omx/state/STATE.md`, `../../../.omx/state/VERIFY_LAST_FAILURE.md`를 읽어 현재 규칙과 상태를 확인한다.
2. 비밀값이 필요한 작업이면 `../../../omx_discord_bridge/.env.discord`가 있는지만 확인하고, 값 자체는 출력하지 않는다.
3. 검증부터 시작할 때는 저장소 루트에서 `pnpm verify:automation` 또는 `pnpm verify:standard`를 실행한다.
4. Windows 운영의 상주 조합은 `bridge + omx-loop`이며 `../../../scripts/run-discord-bridge.ps1`와 `../../../scripts/omx-loop.ps1 -InfiniteMode`를 함께 계속 띄워 둔다.
5. `../../../scripts/ralph-run.ps1`는 필요할 때만 Codex를 한 번 실행하고 끝나는 단발 스크립트라 매 iteration마다 다시 돌리는 기본 루프에 넣지 않는다.

## Runtime Model

- 사용자 -> agent: Discord 메시지는 `../../../.omx/state/DISCORD_INBOX.jsonl`에 들어오고, 최신 메시지 1건만 회의 트리거로 사용한다.
- agent -> agent: 역할 대화는 `planner -> critic -> researcher -> architect -> executor -> verifier` 순서로 진행되고 `../../../.omx/state/TEAM_CONVERSATION.jsonl`에 기록된다.
- 실제 다중 역할 실행기는 Codex 서브에이전트가 아니라 `../../../scripts/omx_autonomous_loop.py` 안에서 호출하는 외부 `omx exec`다.
- Codex에서 이 저장소를 다룰 때는 OMX 런타임을 대체하려 하지 말고, 기존 런타임을 점검하거나 보조하는 방식으로 접근한다.

## Discord Modes

- `OMX_DISCORD_MODE=all`: 현재처럼 역할별 메시지를 모두 Discord에 보낸다.
- `OMX_DISCORD_MODE=signal-only`: watcher ack, 회의 시작/종료, 반복 실패, GitHub 이정표만 Discord에 보내고 상세 역할 대화는 로컬 로그에만 남긴다.
- `OMX_DISCORD_MODE=local-only`: Discord outbound는 끄고 로컬 상태 파일만 갱신한다.

`signal-only`가 기본 권장값이다. 사용자와 agent 사이의 필요한 신호는 유지하면서, agent와 agent 사이의 세부 대화는 `.omx/state/TEAM_CONVERSATION.jsonl`에 남겨 소음을 줄일 수 있다.

## Workflow

1. 상태 확인
   `../../../.omx/state/`와 최근 검증 결과를 읽고, dirty worktree에 `.omx/state/*` 변경이 있으면 임의로 되돌리지 않는다.
2. 브리지 확인
   `python ../../../scripts/test_discord_bridge.py` 또는 `pnpm verify:automation`으로 브리지와 로그 round-trip을 확인한다.
3. 루프 확인
   필요한 경우 `powershell -ExecutionPolicy Bypass -File ../../../scripts/omx-loop.ps1 -InfiniteMode`로 루프를 돌리고 `.omx/runtime/` 상태 파일을 본다.
4. 소음 제어
   Discord에 너무 많이 올라오면 `.env.discord`에 `OMX_DISCORD_MODE=signal-only`를 쓰고 다시 검증한다.
5. 종료 전 검증
   자동화만 건드렸으면 `pnpm verify:automation`, 레포 전반을 건드렸으면 `pnpm verify:standard`를 실행한다.

## Guardrails

- `.env.discord`, `.env`, 토큰, 웹훅 URL은 절대 출력하거나 커밋하지 않는다.
- `.omx/state/*`는 런타임 산출물도 포함하므로, 사용자가 직접 남긴 상태를 함부로 삭제하거나 초기화하지 않는다.
- agent 간 회의 로그는 로컬 JSONL이 source of truth다. Discord는 표시 채널이지 유일 저장소가 아니다.
- Windows 사용자가 직접 실행할 가능성이 높으므로 Bash보다 PowerShell 진입점을 먼저 제시한다.
