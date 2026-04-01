목표:
`/radar` 화면용 섹터 요약 한 문단을 만든다.

반드시 포함:
- `selectedSectorSummary`

작성 방식:
- 숫자, 랭킹, 종목 점수, 컬럼 값은 facts에 있는 값만 사용한다.
- folderTree, watchlistRows, sectorCards, brokerReports, keySchedule, keyIssues, topPicks는 provider가 후처리로 채우므로 억지로 만들어내지 않는다.
- 요약은 현재 선택된 섹터가 왜 우선 검토 대상인지와 어떤 리스크를 같이 봐야 하는지 2~3문장으로 정리한다.
- 직접적인 매수/매도 지시 문구는 쓰지 않는다.
