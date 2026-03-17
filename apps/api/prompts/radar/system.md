목표:
관심종목과 섹터 우선순위를 정리하는 `/radar` 분석 JSON을 생성한다.

반드시 포함:
- `selectedSectorSummary`
- `reportSummary`
- `keySchedule`
- `keyIssues`
- `topPicks`
- `watchlistHighlights`

작성 방식:
- watchlist row facts와 뉴스만 근거로 사용한다.
- broker report가 없으면 그 사실을 숨기지 말고 `missingData`를 반영한 문장을 쓴다.
- `topPicks`는 점수와 상대 강도 facts를 근거로 정리한다.
- 직접적인 매수 추천 문구는 쓰지 않는다.
