1. PR checks가 모두 통과했는지 확인하고 실패가 있으면 같은 브랜치와 같은 PR에 수정 커밋을 올린다.
2. PR이 `develop`에 병합되면 `develop`을 최신화한 뒤 이슈 #162용 새 브랜치를 만든다.
3. 한국 OpenDART 공시와 미국 SEC filings 또는 회사 이벤트 피드를 확장한다.
4. `/news`, `/calendar`, `/stocks/[symbol]`에서 확장된 공시 데이터가 보이는지 API smoke와 E2E를 추가한다.
