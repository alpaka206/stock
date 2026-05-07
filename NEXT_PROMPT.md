1. release PR #174를 사용자가 main에 수동 merge했는지 확인한다.
2. main merge 후 production 배포 완료를 기다린다.
3. `https://stock-radar-board.vercel.app/overview`, `/radar`, `/stocks/NVDA`, `/history`를 직접 확인한다.
4. production 확인 결과와 남은 리스크를 `STATE.md`에 기록한다.
5. #160 후속으로 overview/news/calendar provider builder 분리를 진행한다.
