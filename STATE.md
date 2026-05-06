현재 사실
- `develop` 최신 커밋 `5b14ab2` 기준으로 브랜치 `issue/158-technical-indicators-patterns`에서 작업 중이다.
- 이슈 #158은 기술지표와 패턴 분석 엔진 구현, 이슈 #164는 Windows 표준 검증 Python 실행 경로 복구를 다룬다.
- 종목 상세 계약에 `chartOverlays`, `technicalMetrics`, `patternCards`가 추가되었다.
- API real provider는 가격 시계열에서 MA5, MA10, MA20, MA60, RSI14, MACD, 지지선, 저항선, 거래량 배수를 계산한다.
- mock provider와 웹 fixture도 같은 필드를 제공해 실데이터가 없을 때 화면 구조가 유지된다.
- 종목 상세 화면은 선택된 룰 preset과 연결된 이동평균선을 차트에 표시하고, 기술 지표 체크와 패턴 유사도 카드를 별도 패널로 보여준다.
- `scripts/run-python.mjs`와 `scripts/verify_workspace.py` 수정으로 Windows의 Microsoft Store Python 실행 별칭 문제를 우회했다.

최근 검증 결과
- `pnpm verify:automation` 통과.
- `pnpm verify:standard` 통과.
- 표준 검증 안에서 text quality, automation, web lint, web typecheck, web build, contract parity, API py_compile, API smoke가 모두 통과했다.
- API smoke에서 `/readyz`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`, `/instruments/search?q=nvda`가 200 응답을 반환했다.

남은 리스크
- 기술지표 계산은 현재 일봉 시계열 기반 1차 구현이며, 분봉이나 사용자 정의 기간 선택은 아직 없다.
- 패턴 유사도는 규칙 기반 점수로 시작했으며, 장기적으로 백테스트나 사례 라이브러리 기반 보강이 필요하다.
- PR 생성 후 GitHub Actions와 Vercel checks 결과를 추가 확인해야 한다.

다음 우선순위
- 현재 변경사항을 `feat: 기술지표 패턴 분석 구현` 커밋으로 정리한다.
- 브랜치를 원격에 push하고 `develop` 대상 PR을 생성한다.
- 다음 브랜치에서는 이슈 #159의 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` E2E 검증을 추가한다.
- 이후 리서치 스냅샷 영속 저장소와 공시 데이터 소스 확장 작업을 순차 진행한다.
