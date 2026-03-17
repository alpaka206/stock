목표:
단일 종목을 깊게 읽는 `/stocks/[symbol]` 분석 JSON을 생성한다.

반드시 포함:
- `score`
- `signals`
- `flowSummary`
- `optionsShortSummary`
- `issueSummary`
- `chartNotes`
- `risks`

작성 방식:
- 점수는 입력 facts의 scoreModel과 모순되지 않아야 한다.
- 흐름/공매도/옵션 데이터가 없으면 unavailable 상태를 분명하게 적는다.
- 기술적 해석은 가격 흐름, 변동성, 거래량 facts 안에서만 작성한다.
- 신호 문장은 짧고 검증 가능해야 한다.
