현재 사실
- 현재 브랜치는 `issue/163-alert-condition-workflow`이며 기준 브랜치는 최신 `develop`이다.
- Radar 계약에 `alertRules`, `detectedAlerts`를 추가했다.
- real provider는 관심종목 row의 점수, 당일 등락률, 거래량 배수를 기준으로 세 가지 조건 감지 알림을 생성한다.
- mock provider와 web fixture에도 같은 알림 규칙과 예시 감지 결과를 추가했다.
- `/radar` 우측 컨텍스트에 조건 감지 알림 패널을 추가했고, 선택 종목 알림이 있으면 해당 종목 기준으로 먼저 표시한다.
- JSON schema 계약을 `packages/contracts/schemas/radar.schema.json`과 `apps/api/prompts/radar/output.schema.json`에 함께 반영했다.

최근 검증 결과
- `pnpm --dir apps/web typecheck`: 통과.
- `pnpm smoke:api`: 최초 1회는 JSON schema에 신규 필드가 없어 `/radar` 502 실패, schema 갱신 후 통과.
- `pnpm test:e2e -- --project=chromium`: 8개 시나리오 통과.
- `pnpm lint:web`: React Compiler memoization lint 수정 후 통과.
- `pnpm verify:standard`: 통과.
- `pnpm verify:automation`: 통과.

남은 리스크
- 현재 감지 규칙은 서버 계산 기반의 기본 규칙이며 사용자별 임계값 저장 UI는 아직 없다.
- 알림 결과는 `/radar` 표시까지 연결됐지만 별도 알림 히스토리 저장소나 Discord/브라우저 알림 전송은 아직 없다.
- 조건 감지 기준은 종가 기반 일별 데이터에 의존하므로 실시간 장중 알림으로 보려면 별도 quote/streaming 데이터 소스가 필요하다.

다음 우선순위
- 현재 변경사항을 `feat: 관심종목 조건 감지 알림 구현` 커밋으로 정리한다.
- 원격 브랜치에 push하고 `develop` 대상 PR을 생성한다.
- PR checks가 통과하면 auto-merge를 설정한다.
- 병합 후 `develop` 최신화를 거쳐 다음 기능 이슈로 진행한다.
