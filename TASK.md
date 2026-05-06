현재 라운드 목표
- 이슈 #160의 첫 번째 리팩터링 단위로 `/radar` real provider 조립 책임을 별도 builder 모듈로 분리한다.
- `dict[str, Any]` 중심 경계를 줄이기 위해 Radar 입력/출력 TypedDict를 추가한다.
- 동작 변화 없이 표준 검증과 자동화 검증을 통과한 상태로 `develop` 대상 PR을 생성한다.

완료 조건
- `apps/api/app/services/providers/radar_builders.py`가 Radar watchlist, sector card, issue, alert, folder tree 조립을 담당한다.
- `RealResearchProvider._get_radar_v2`는 새 builder 모듈을 사용한다.
- `scripts/test_radar_builders.py`가 표준 검증 API 단계에 포함된다.
- `pnpm verify:standard`와 `pnpm verify:automation`이 통과한다.
- PR 본문에는 이 작업이 #160의 부분 리팩터링임을 명시한다.
