현재 사실
- 현재 브랜치는 `issue/160-provider-module-types`이다.
- `develop`은 PR #169 `feat: 관심종목 조건 감지 알림 구현`까지 fast-forward 되어 있다.
- 완료된 이슈 #134, #158, #159, #161, #162, #163, #164는 병합 PR 기준으로 정리해 닫았다.
- 열린 PR은 없고, #135는 이미 `develop_loop`에 merge된 상태다.
- Dependabot PR은 현재 열린 항목이 없으며, 과거 실패 Dependabot PR들은 닫힌 상태다.
- #160의 첫 리팩터링으로 Radar builder 전용 모듈과 TypedDict 경계를 추가했다.

최근 검증 결과
- `node scripts/run-python.mjs scripts/test_radar_builders.py`: 통과.
- `node scripts/run-python.mjs -m py_compile apps/api/app/services/providers/radar_builders.py apps/api/app/services/providers/real.py scripts/test_radar_builders.py scripts/verify_workspace.py`: 통과.
- `pnpm smoke:api`: 통과.
- `pnpm verify:standard`: 통과.
- `pnpm verify:automation`: 통과.

남은 리스크
- 이번 PR은 #160의 Radar 범위 리팩터링이며, stock detail/history/overview builder 분리는 아직 남아 있다.
- `RealResearchProvider` 내부에는 과거 v1 흐름의 unreachable code와 중복 private builder가 일부 남아 있다.
- TypedDict는 runtime 검증이 아니므로 API 계약 검증은 기존 Pydantic schema와 JSON schema parity에 계속 의존한다.

다음 우선순위
- 현재 변경사항을 `refactor: 레이더 provider builder 타입 경계 분리` 커밋으로 정리한다.
- `develop` 대상 PR을 만들고 본문에 `Refs #160`으로 부분 진행임을 남긴다.
- 병합 후 같은 #160 후속 브랜치에서 stock detail/history builder 분리와 unreachable code 제거를 이어간다.
