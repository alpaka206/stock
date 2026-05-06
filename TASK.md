현재 라운드 목표
- `develop` 최신 기준에서 종목 상세 화면의 기술지표, 패턴 분석, 차트 보조선을 실제 시계열 기반으로 연결한다.
- Windows 로컬에서도 `pnpm verify:automation`, `pnpm verify:standard`가 실행되도록 검증 러너를 복구한다.
- 이슈 #158, #164 변경을 커밋하고 `develop` 대상 PR로 올린다.

완료 조건
- `/stocks/[symbol]` API 응답에 `chartOverlays`, `technicalMetrics`, `patternCards`가 포함된다.
- 종목 상세 화면에서 이동평균선, 기술 지표 체크, 패턴 유사도 카드가 렌더링된다.
- `pnpm verify:automation`과 `pnpm verify:standard`가 통과한다.
- 브랜치 `issue/158-technical-indicators-patterns`가 원격에 push되고 `develop` 대상 PR이 생성된다.
