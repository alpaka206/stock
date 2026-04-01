# 웹앱 전용 지침

## 기술 스택
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- AG Grid Community
- TanStack Query
- 다크모드 기본
- 금융 차트 라이브러리는 차트 전용 모듈로 분리

## 웹앱 설계 원칙
- 페이지 shell은 가능한 한 Server Component로 시작한다.
- 차트, 그리드, 필터, 드래그/리사이즈, 사용자 프리셋은 Client Component로 분리한다.
- URL로 공유 가능한 상태(검색, 필터, 정렬, 날짜 범위)는 search params로 유지한다.
- 숫자는 정렬 가능한 구조와 고정 폭 숫자 스타일을 고려한다.
- 상승/하락/중립은 색상만으로 구분하지 않는다. 아이콘/텍스트/보조 라벨을 함께 둔다.

## 페이지별 레이아웃 원칙
### /overview
- 상단: 지수 스트립
- 중단: 시황 요약, 히트맵, 뉴스
- 하단: 섹터 강도, 리스크 카드

### /radar
- 좌측: 관심종목 폴더/태그/트리
- 중앙: AG Grid Community 기반 관심종목 그리드
- 우측: 섹터 요약, 리포트 요약, 일정, Top Pick

### /stocks/[symbol]
- 중앙 대형 차트가 1순위 시각 요소
- 우측 조건 패널은 사용자의 보조지표 프리셋과 감지 규칙을 가진다
- 하단은 탭 구조로 점수/수급/옵션·공매도/이슈/시나리오를 나눈다

### /history
- 상단 필터(종목, 날짜 범위)
- 중앙 리플레이 차트
- 우측 또는 하단 타임라인
- 변곡점 설명 카드와 중복 지표 요약 카드 포함

## AG Grid Community 원칙
- 이 프로젝트는 표가 아니라 grid를 핵심 인터랙션으로 본다.
- 무료 범위를 유지하기 위해 AG Grid Community만 사용한다.
- 정렬, 필터, 행 선택, 컬럼 추가/제거, 커스텀 셀, 상태 저장/복원을 기본 고려한다.
- 폴더/섹터/시장 기준 group view는 AG Grid Enterprise row grouping에 의존하지 말고 아래 방식으로 구현한다.
  - 좌측 폴더 트리
  - 상단 view mode 토글
  - 섹션형 스택 그리드 또는 사전 그룹화된 데이터셋
  - URL/search params 기반 그룹 필터
- 컬럼 토글 UI는 Community column menu에 의존하지 말고 커스텀 툴바/시트/드롭다운으로 구현한다.
- localeText는 한국어 우선으로 설정한다.
- grid 설정은 `features/grid/` 아래에서 공통화한다.

## 변경 시 같이 업데이트할 것
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/changes/CHANGELOG_APPEND_ONLY.md`
