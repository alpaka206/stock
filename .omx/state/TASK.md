# 작업 계약

- PRIMARY_TASK: 1단계 Discord 기반 agent 회의형 운영을 완성하고, 2단계에서 주식 데이터·API·FE·BE 기능을 완성하고, 3단계에서 QA·배포·배포 사이트 직접 확인까지 끝낸 뒤 추가 가치가 높은 기능과 점검을 이어간다.
- MIN_EXIT_CONDITION: 1단계에서 Discord를 통해 agent들이 서로 읽고 역할별로 응답하는 회의 흐름이 실제로 확인된다. 2단계에서 차트, 실시간 글로벌 뉴스, 공시, API 연동, FE/BE 연결이 end-to-end로 동작한다. 3단계에서 QA 완료, main 반영, 배포 사이트의 FE/BE 직접 확인, 후속 개선 기록까지 끝난다.
- AUTO_CONTINUE_POLICY: 최소 종료 조건을 충족할 때까지 가장 작고 검증 가능한 다음 작업을 스스로 고르고 계속 진행한다.
- RELEASE_TO_MAIN_POLICY: auto-merge-if-green
- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- MULTI_AGENT_CONSENSUS: `planner -> critic -> researcher -> architect -> executor -> verifier`
