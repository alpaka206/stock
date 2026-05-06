1. #160 stock/history provider builder 분리 PR을 `develop` 대상으로 생성한다.
2. PR checks가 통과하면 자동 병합하고 `develop`을 최신화한다.
3. `pnpm verify:release`를 실행한다.
4. `develop -> main` 수동 merge PR을 생성하고 Discord에 보고한다.
5. 배포 사이트에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history`를 직접 확인한다.
