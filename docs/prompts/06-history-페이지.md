# 목표
`/history` 히스토리/이벤트 리플레이 화면을 구현한다.

# 참고 문서
- docs/architecture/page-manifest.yaml
- docs/architecture/component-manifest.yaml
- docs/design/design-memory.md

# 필수 UI
- 종목 + 날짜 범위 선택
- 과거 차트 리플레이
- 이벤트/뉴스 타임라인
- 급등/급락 이유 요약 카드
- 중복 지표 설명 카드

# 필수 기능
- 날짜 기준으로 차트와 타임라인을 동기화
- 특정 이벤트를 클릭하면 차트 포커스 이동
- 변곡점에서 겹친 보조지표 신호 설명
- 과거 움직임 이유를 JSON + UI로 제공

# 완료 조건
- 사용자가 과거 급등/급락 이유를 쉽게 다시 읽을 수 있다.
- 차트와 타임라인이 연결된다.
- 관련 문서와 changelog를 갱신한다.
