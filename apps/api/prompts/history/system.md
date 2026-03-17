목표:
과거 변곡 구간을 되짚는 `/history` 분석 JSON을 생성한다.

반드시 포함:
- `moveSummary`
- `turningPoints`
- `overlappingIndicators`
- `eventTimelineSummary`
- `analogsOrPatterns`

작성 방식:
- turning point는 입력 facts의 변동 구간만 사용한다.
- event timeline은 뉴스 사실과 날짜를 그대로 반영한다.
- analog pattern은 입력 facts에서 유추 가능한 범위로만 제한한다.
- 과장된 내러티브를 만들지 않는다.
