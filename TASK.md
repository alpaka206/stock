현재 라운드 목표
- 이슈 #163 기준으로 레이더 관심종목 조건 감지 알림 워크플로를 구현한다.
- 감지 규칙, API 계약, mock/dev fixture, `/radar` UI, E2E 검증을 하나의 PR로 `develop`에 올린다.

완료 조건
- `/radar` 응답에 `alertRules`, `detectedAlerts`가 포함되고 schema parity와 API smoke가 통과한다.
- `/radar` 화면에서 조건 감지 알림 패널과 알림 카드가 표시된다.
- `pnpm test:e2e -- --project=chromium`, `pnpm verify:automation`, `pnpm verify:standard`가 통과한다.
- 변경사항을 커밋하고 `issue/163-alert-condition-workflow`에서 `develop` 대상 PR을 생성한다.
