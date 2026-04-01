# 목표
`/overview` 화면을 구현한다.

# 참고 문서
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- docs/design/design-memory.md

# 필수 UI
- 지수 스트립
- AI 시황 요약 카드
- 시장 히트맵
- 뉴스 패널
- 섹터 강도 패널
- 리스크 배너

# API 요구
- 지수/환율/해외지수
- 뉴스 요약
- 섹터 강도
- 시장 요약 JSON

# 완료 조건
- overview 화면만 봐도 오늘 시장이 어떤지 10초 안에 읽힌다.
- 각 카드가 다른 화면으로 자연스럽게 이동된다.
- 관련 manifest, changelog를 갱신한다.
