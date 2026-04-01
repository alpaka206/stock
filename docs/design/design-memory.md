# 디자인 메모리

이 문서는 Codex가 매번 사용자에게 제품 방향을 다시 묻지 않도록 현재 저장소의 화면 우선순위와 UX 원칙을 기록한다. 과거 결정을 덮어쓰지 않고 아래 변경 기록에 누적한다.

## 현재 기준
- 제품 성격: 금융 리서치 워크스페이스
- 기본 모드: 다크 모드 우선
- 기본 언어: 한국어
- 핵심 UX: 뉴스, 차트, 섹터, 수급, 옵션/공매도, 점수, 과거 이벤트를 한 흐름으로 보는 분석 화면
- 구조 원칙: 4개 메인 페이지를 고정하고, route는 얇게 유지하며 feature 내부에서 화면 모델과 UI를 분리한다.

## 공통 시각 원칙
- 숫자와 퍼센트는 어디서 보더라도 바로 비교 가능해야 한다.
- 색만으로 상승/하락을 구분하지 않고, 레이블과 숫자를 같이 둔다.
- 카드형 레이아웃과 dense grid가 공존하므로 시선 흐름은 좌에서 우, 상에서 하로 분명해야 한다.
- 실데이터가 없는 영역은 fabricated value 대신 unavailable 상태와 missingData 이유를 보여준다.
- AG Grid는 실제 작업 영역으로 취급한다. 임시 table 대체를 허용하지 않는다.

## 페이지별 메모

### overview
- 첫 화면은 10초 안에 오늘 시장 방향이 읽혀야 한다.
- 지수 스트립과 AI 시황 요약 카드가 가장 먼저 보여야 한다.
- 뉴스, 섹터 강도, 리스크 카드가 자연스럽게 `/radar`, `/stocks/[symbol]`, `/history`로 이어져야 한다.

### radar
- 좌 / 중 / 우 3단 구조를 유지한다.
- 왼쪽은 폴더와 태그, 중앙은 AG Grid, 오른쪽은 선택 섹터 컨텍스트다.
- grid는 정렬, 필터, 컬럼 토글, flat / sector view, 저장된 preset까지 포함한 작업 화면이어야 한다.
- enterprise grouping 대신 pre-grouped stacked grid로 섹터 view를 만든다.

### stock detail
- 중앙 대형 차트가 주인공이고, 우측 규칙 panel은 보조 역할이다.
- 검색, 관련 종목 점프, 이벤트 마커, indicator guide가 모두 차트 중심 흐름을 보조해야 한다.
- 총점만이 아니라 breakdown과 confidence를 같이 보여준다.
- 수급과 옵션/공매도 데이터가 없으면 비워 두지 말고 unavailable 이유를 보여준다.

### history
- 차트와 이벤트 타임라인이 같은 선택 상태를 공유해야 한다.
- 특정 이벤트를 누르면 차트 포커스가 이동하고, 이전 / 다음 step 이동이 쉬워야 한다.
- 급등 / 급락 이유 카드와 중복 지표 카드가 “왜 그날 움직였는가”를 다시 읽게 해야 한다.

## 구현 메모
- URL로 공유해야 하는 상태만 search params에 둔다.
- 사용자 preset은 localStorage에 저장한다.
- 차트는 공통 `ResearchLineChart`를 확장해 active point, marker, highlight range를 지원한다.
- 숫자와 시계열은 provider에서 결정론적으로 만들고, LLM은 thesis / moveSummary / sector summary 같은 요약 문장 위주로 사용한다.

## 변경 기록

### 2026-03-15
- 4개 메인 화면 구조와 문서 우선 작업 방식을 고정했다.

### 2026-03-16
- 공통 shell, theme/query provider, AG Grid Community 공통 래퍼를 추가했다.
- 다크 모드와 dense research layout을 기본 시각 방향으로 잡았다.

### 2026-03-18
- overview를 “지수 스트립 → AI 시황 요약 → heatmap → 뉴스 / 섹터 / 리스크” 흐름으로 고정했다.

### 2026-03-21
- radar를 폴더 / 태그 / preset + AG Grid + 섹터 컨텍스트 3단 작업 화면으로 구현했다.
- stock detail을 검색, 대형 차트, 이벤트 마커, 규칙 preset, breakdown 탭 구조로 확장했다.
- history를 symbol / range 기반 리플레이 화면으로 구현하고 차트와 타임라인을 동기화했다.
- 세 화면 모두 API 우선 + fixture fallback 구조, localStorage preset, search params 기반 상태 흐름을 사용한다.
