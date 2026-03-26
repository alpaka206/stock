# 목표
`/radar` 화면을 구현한다. 이 화면은 관심종목과 섹터 분석을 동시에 수행하는 핵심 작업 화면이다.

# 참고 문서
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- docs/design/design-memory.md
- apps/web/AGENTS.md

# 필수 UI
- 좌측: 폴더/태그/트리
- 중앙: AG Grid 기반 관심종목 그리드
- 우측: 선택 섹터 요약, 리포트 요약, 일정, 주요 이슈, top pick

# 필수 기능
- 폴더화
- 컬럼 토글
- 정렬
- 필터
- 섹터 기준 group view
- 선택된 섹터에 따라 우측 패널 갱신
- 저장된 뷰 프리셋

# 제약
- grid는 이 프로젝트의 핵심 UX이므로 임시 table로 대체하지 않는다.
- 추후 서버사이드 데이터 모델로 확장 가능한 형태로 짠다.

# 완료 조건
- 레이아웃이 좌/중/우 3단 구조로 동작한다.
- AG Grid가 실제 작업 화면처럼 동작한다.
- 관련 문서와 changelog를 갱신한다.
