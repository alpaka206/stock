# 목표
`/stocks/[symbol]` 종목 분석 워크스테이션을 구현한다.

# 참고 문서
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- docs/design/design-memory.md

# 필수 UI
- 종목 검색
- 대형 가격 차트
- 보조지표 표시
- 우측 사용자 규칙/프리셋 패널
- 하단 탭:
  - 점수
  - 수급
  - 공매도/옵션 비율
  - 종목/섹터/시황 이슈 분석

# 필수 기능
- 티커/종목번호/종목명 검색
- 보조지표 6개 이상 규칙 설정
- 점수 breakdown
- 수급 요약
- 공매도 및 옵션 비율 영역
- 사용자 프리셋 저장

# 완료 조건
- 한 종목의 핵심 판단 근거가 한 화면에 모인다.
- 차트가 중심이고 우측 규칙 패널이 보조한다.
- 점수 총합만이 아니라 breakdown과 confidence가 보인다.
