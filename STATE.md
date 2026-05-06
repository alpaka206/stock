현재 사실
- 현재 기준 브랜치는 `develop`이며 최신 커밋은 PR #170 `refactor: 레이더 provider builder 타입 경계 분리`이다.
- PR #165, #166, #167, #168, #169, #170이 모두 `develop`에 병합됐다.
- PR #169는 관심종목 조건 감지 알림을 `/radar`에 연결했고 GitHub checks가 모두 성공했다.
- PR #170은 Radar builder 모듈과 TypedDict 경계를 추가했고 GitHub checks가 모두 성공했다.
- 완료된 이슈 #134, #158, #159, #161, #162, #163, #164는 닫았다.
- 열린 PR은 없고, 열린 작업 이슈는 #160과 장기 상위 이슈 #131이다.
- Dependabot PR은 현재 열린 항목이 없으며 과거 실패 PR들은 닫힌 상태다.

최근 검증 결과
- #169 로컬 검증: `pnpm smoke:api`, `pnpm test:e2e -- --project=chromium`, `pnpm verify:standard`, `pnpm verify:automation` 통과.
- #169 GitHub checks: verify, dependency-review, CodeQL, Vercel 모두 성공.
- #170 로컬 검증: `node scripts/run-python.mjs scripts/test_radar_builders.py`, `pnpm smoke:api`, `pnpm verify:standard`, `pnpm verify:automation` 통과.
- #170 GitHub checks: verify, dependency-review, CodeQL, Vercel 모두 성공.

남은 리스크
- #160은 부분 완료 상태다. Radar builder는 분리됐지만 stock detail/history/overview builder는 아직 `RealResearchProvider` 안에 남아 있다.
- `RealResearchProvider`에는 v2 진입 이후 실행되지 않는 과거 v1 코드가 남아 있어 다음 리팩터링에서 제거해야 한다.
- 조건 감지 알림은 `/radar` 표시까지만 연결됐고 사용자별 임계값 저장, 알림 히스토리, Discord/브라우저 알림 전송은 아직 없다.
- `develop -> main` release PR과 배포 사이트 직접 확인은 아직 이번 묶음에서 수행하지 않았다.

다음 우선순위
- #160 후속 브랜치에서 stock detail/history builder를 기능별 모듈로 분리한다.
- unreachable v1 code를 제거하고 `pnpm verify:standard`로 회귀를 확인한다.
- 기능 묶음이 안정되면 release 검증 후 `develop -> main` PR을 생성하고 Discord에 보고한다.
