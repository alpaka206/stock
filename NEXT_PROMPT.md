1. #175 종목 상세 API 버전 차이 fallback PR을 `develop`에 병합한다.
2. release PR #174가 최신 `develop` 커밋을 포함하는지 확인하고 checks를 재확인한다.
3. 사용자가 #174를 main에 수동 merge한 뒤 production 배포 완료를 기다린다.
4. `https://stock-radar-board.vercel.app/overview`, `/radar`, `/stocks/NVDA`, `/history`를 다시 직접 확인한다.
5. production 확인 결과와 남은 리스크를 `STATE.md`에 기록한다.
