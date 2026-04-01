목표:
`/history` 화면에서 과거 급등/급락 이유를 다시 읽을 수 있게 하는 요약을 만든다.

반드시 포함:
- `moveSummary`

작성 방식:
- priceSeries, eventTimeline, moveReasons, overlappingIndicators는 provider가 facts에서 직접 채우므로 새 이벤트나 새 수치를 만들지 않는다.
- moveSummary는 과거 움직임의 주된 상승/하락 원인과 현재 다시 볼 때 체크할 리스크를 2~3문장으로 정리한다.
- 과장된 내러티브를 만들지 않고, facts에 없는 뉴스/지표/패턴은 추가하지 않는다.
