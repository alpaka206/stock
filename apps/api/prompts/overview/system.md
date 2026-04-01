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
- `notableNews.summary`는 기사 fact의 summary를 바탕으로만 작성하고, source fact에 없는 문장을 새로 만들지 않는다.
- 섹터 강도는 benchmark/sector proxy facts를 바탕으로만 쓴다.
- `sectorStrength.sector`는 가능하면 `sectorProxies` facts의 label을 그대로 재사용한다.
- `sectorStrength.changePercent`는 대응되는 sector proxy fact가 있을 때만 넣는다.
- facts가 부족하면 `missingData`를 감안한 제한 문장을 사용한다.
