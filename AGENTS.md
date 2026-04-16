# 저장소 자율 작업 계약

저장소 목적: 주식 리서치 워크스페이스

메인 고정 화면
1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

먼저 읽을 문서
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/codex/prompt-order.md`

## 최상위 계약
- PRIMARY_TASK: 1단계 Discord 기반 agent 회의형 자동화 완성. 2단계 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 를 중심으로 주식 데이터·API·FE·BE 기능 완성. 3단계 QA, GitHub 흐름, 배포, 실배포 확인까지 마무리. 4단계 남은 리스크와 후속 기능을 문서와 저널에 기록.
- MIN_EXIT_CONDITION: 1단계에서 허용된 Discord 사용자 메시지 1건이 최신 트리거로만 소비되고 `planner -> critic -> researcher -> architect -> executor -> verifier` 응답이 실제 Discord와 `.omx/state/TEAM_CONVERSATION.jsonl` 에 남는다. 2단계에서 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 와 관련 API·FE·BE 연결이 end-to-end 로 동작하고 차트, 뉴스, 공시, 히스토리 핵심 기능이 검증된다. 3단계에서 `pnpm verify:standard`, release 검증, `develop -> main` 반영, 배포 사이트 FE/BE 직접 확인이 끝난다. 4단계에서 남은 리스크와 후속 가치 작업이 한국어 문서로 정리된다.
- AUTO_CONTINUE_POLICY: 최소 종료 조건을 충족할 때까지 가장 작고 검증 가능한 다음 작업을 스스로 고르고 계속 진행
- RELEASE_TO_MAIN_POLICY: auto-merge-if-green
- ENABLE_GITHUB_AUTOMATION: true
- ISSUE_PR_POLICY: issue-first branch -> develop, develop -> main release pr
- REVIEW_FEEDBACK_POLICY: same-branch same-pr follow-up
- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`

## 단계별 목표
1. Discord 회의형 자동화
- 실제 Discord 채널에서 사용자 메시지 수집, latest-only 처리, superseded 정리, 역할별 회신, 로컬 대화 로그 보존, verify gate 실행이 이어져야 한다.
2. 제품 기능
- `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 기준으로 실제 데이터, 화면, API, 계약, 연결 상태가 모두 맞아야 한다.
3. QA와 배포
- 표준 검증, release 검증, 브랜치/PR 흐름, develop 반영, main release PR, 배포 사이트 실측까지 끝나야 한다.
4. 후속 확장
- 남은 리스크, 운영 메모, 다음으로 가치가 높은 기능을 문서화해 다음 세션이 바로 이어질 수 있어야 한다.

## 문서 작성 규칙
- `TASK.md` 는 현재 라운드의 목표와 완료 조건만 짧게 유지한다.
- `BACKLOG.md` 는 바로 실행할 체크리스트만 남기고, 끝난 항목은 `[x]` 로 닫는다.
- `STATE.md` 는 현재 사실, 최근 검증, 리스크, 다음 우선순위를 한국어로 기록한다.
- `NEXT_PROMPT.md` 는 다음 세션에서 바로 실행할 3~5개 액션만 적는다.
- 완료 조건은 반드시 관측 가능한 화면, API, 로그, 명령 기준으로 쓴다.

## 핵심 규칙
- 사용자에게 불필요한 확인 질문을 하지 않는다.
- 큰 작업은 작은 검증 단위로 쪼개고, 매 단위마다 상태와 저널을 갱신한다.
- 구현보다 검증과 비밀 보호를 우선한다.
- 출처 없는 가격, 뉴스, 레벨, 점수를 만들지 않는다.
- `omx_discord_bridge/.env.discord` 는 읽기 전용 비밀 입력으로만 다룬다.
- 사용자가 직접 읽거나 작성해야 하는 요약, 체크리스트, 상태 파일은 한국어 우선으로 남긴다.
- 작업 종료 전 문서와 상태 파일에 이중 물음표, raw unicode escape, 한글 깨짐이 없는지 확인한다.

## 다중 agent 합의
- 큰 기능, 위험도 높은 변경, 배포 전에는 `planner -> critic -> architect -> executor` 순서의 짧은 합의 루프를 먼저 수행한다.
- 필요하면 역할을 추가로 소환해 병렬 조사, 코드 리뷰, 테스트, 문서 정리를 분담한다.
- 합의 결과는 `.omx/journal/` 또는 `.omx/state/*` 에 남긴다.

## 무한 실행
- `scripts/omx-loop.sh` 는 `MAX_ITERATIONS=0` 또는 `INFINITE_MODE=true` 이면 무한 루프로 동작한다.
- 각 iteration 기록에는 시작 시각, 선택한 작업, 변경 대상, 검증 결과, 다음 액션을 한국어로 상세하게 남긴다.
- 같은 실패가 3회 연속 반복되면 같은 방법 반복을 중지하고 원인과 우회책을 기록한다.

## 검증 실패 규칙
- guard, lint, build, test, smoke, release 실패는 모두 최우선 복구 대상이다.
- 실패 원인은 `.omx/state/VERIFY_LAST_FAILURE.md` 에 기록한다.
- 실패한 명령을 다시 통과시킨 뒤 넓은 게이트를 재실행한다.

## Git 규칙
- permanent branch: `main`, `develop`
- permanent branch 직접 push, force push, hard reset, 삭제 금지
- 작업은 `develop` 기준 issue-linked branch 우선
- 리뷰 피드백은 같은 브랜치와 같은 PR에 반영
- RELEASE_TO_MAIN_POLICY 는 main 자동화의 단일 제어점

## 리뷰 게이트
1. 구현
2. lint / build / test
3. Codex 코드 리뷰
4. blocking issue 없음 또는 approve
5. 그때만 push / PR / develop 반영
