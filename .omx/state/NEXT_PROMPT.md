# 다음 작업 지침

현재 최상위 목표는 `AGENTS.md` 의 `PRIMARY_TASK` / `MIN_EXIT_CONDITION` 이다.
다음 세션은 장기 목표를 직접 바꾸지 말고, 아래 순서로 현재 서비스 상태를 복구·검증하는 데 집중한다.

1. Render API `https://stock-9i67.onrender.com` 의 `/overview`, `/radar` 초기 지연과 타임아웃 가능성을 먼저 확인하고, 원인을 코드 기준으로 줄인 뒤 연속 재검증한다.
2. Discord 회의형 루프를 실제 사용자 메시지 1건 기준으로 다시 실행해 한국어 역할 대화, `reply_to`, superseded 처리, UTF-8 출력이 유지되는지 확인한다.
3. 로컬 자동화 변경분을 issue-linked branch에 정리해서 GitHub 자동 issue -> branch -> PR -> develop -> main 흐름이 다시 실행 가능하도록 만든다.
4. 프런트 `https://stock-mu-seven.vercel.app` 와 백엔드 `https://stock-9i67.onrender.com` 의 핵심 경로를 다시 점검하고, 결과와 남은 리스크를 `.omx/state/STATE.md` 와 `.omx/journal/` 에 한국어로 기록한다.

## 재확인할 기준 경로

- 프런트: `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`
- 백엔드: `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`, `/news`, `/calendar`

## 현재 기준 판단

- 프런트 핵심 경로는 2026-04-14 재확인에서 모두 200 응답을 돌려줬다.
- 백엔드는 첫 확인에서 `/overview`, `/radar` 가 타임아웃이었고, 같은 세션 재확인에서는 200으로 회복됐다.
- 따라서 다음 iteration의 최우선은 “기능 추가”보다 “핵심 경로 초기 지연 안정화 + 자율 운영 루프 실측 검증”이다.
