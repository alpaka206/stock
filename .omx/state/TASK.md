# 작업 계약

- PRIMARY_TASK: 1단계 Discord 기반 agent 회의형 운영 완성, 2단계 주식 데이터·API·FE·BE 기능 완성, 3단계 QA·배포·배포 사이트 직접 확인까지 마무리한 뒤 추가 가치가 높은 기능과 점검까지 진행
- MIN_EXIT_CONDITION: 1단계에서 Discord를 통해 agent들이 서로 읽고 역할별로 응답하는 회의 흐름이 실제로 확인됨. 2단계에서 차트, 실시간 글로벌 뉴스, 공시, API 연동, FE/BE 연결이 end-to-end로 동작함. 3단계에서 QA 완료, main 반영, 배포 사이트의 FE/BE 직접 확인까지 끝남. 이후 유용한 후속 기능과 추가 점검 결과까지 기록됨.
- AUTO_CONTINUE_POLICY: 최소 종료 조건을 충족할 때까지 가장 작고 검증 가능한 다음 작업을 스스로 고르고 계속 진행
- RELEASE_TO_MAIN_POLICY: auto-merge-if-green
- ENABLE_DISCORD_BRIDGE: true
- DISCORD_ENV_FILE: `omx_discord_bridge/.env.discord`
- MULTI_AGENT_CONSENSUS: `planner -> critic -> researcher -> architect -> executor -> verifier`

## 이번 세션 결과

- 배포 관련 핵심 PR `#32`, `#33`, `#34` 를 모두 처리했다.
- 프로덕션 프런트와 원격 백엔드의 핵심 경로를 실제로 확인했다.
- 현재 기준으로 배포 사이트는 정상 동작 상태다.
