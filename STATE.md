현재 사실
- PR #165, #166, #167, #168, #169, #170, #171, #172가 모두 `develop`에 병합됐다.
- PR #172는 stock detail/history replay builder를 `stock_builders.py`, `history_builders.py`로 분리했다.
- PR #172는 `RealResearchProvider`의 `get_radar`, `get_stock_detail`, `get_history` 뒤에 남아 있던 도달 불가능한 v1 본문을 제거했다.
- 열린 PR은 없고, 열린 작업 이슈는 #160과 장기 상위 이슈 #131이다.
- Dependabot PR은 현재 열린 항목이 없으며 과거 실패 PR들은 닫힌 상태다.

최근 검증 결과
- #172 로컬 검증: `node scripts/run-python.mjs scripts/test_stock_history_builders.py`, `node scripts/run-python.mjs scripts/test_radar_builders.py`, `node scripts/run-python.mjs scripts/text_quality_guard.py` 통과.
- #172 로컬 검증: `pnpm verify:automation`, `pnpm verify:standard` 통과.
- #172 GitHub checks: verify, dependency-review, CodeQL, Vercel 모두 성공했고 `develop`에 병합됐다.

남은 리스크
- #160의 provider 분리는 radar/stock/history 중심으로 완료됐고, overview/news/calendar builder 경계는 아직 더 분리할 여지가 있다.
- 조건 감지 알림은 `/radar` 표시까지만 연결됐고 사용자별 임계값 저장, 알림 히스토리, Discord/브라우저 알림 전송은 아직 없다.
- `develop -> main` release PR, Discord 보고, 배포 사이트 직접 확인은 아직 수행 전이다.

다음 우선순위
- `develop` 최신 상태에서 `pnpm verify:release`를 실행한다.
- `develop -> main` 수동 merge PR을 생성하고 자동 병합을 설정하지 않는다.
- release PR 생성 사실을 Discord에 1회 보고한다.
- 배포 URL에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history` 핵심 경로를 직접 확인한다.
