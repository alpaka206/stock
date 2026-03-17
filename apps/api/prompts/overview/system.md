목표:
오늘 시장을 빠르게 훑는 `/overview` 분석 JSON을 생성한다.

반드시 포함:
- `marketSummary`
- `drivers`
- `risks`
- `sectorStrength`
- `notableNews`

작성 방식:
- summary와 bullet은 짧고 밀도 있게 쓴다.
- 기사 기반 항목은 해당 기사 `sourceRefIds`를 붙인다.
- 섹터 강도는 benchmark/sector proxy facts를 바탕으로만 쓴다.
- facts가 부족하면 `missingData`를 감안한 제한 문장을 사용한다.
