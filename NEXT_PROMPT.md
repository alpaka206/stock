1. 문서 상태 정리 PR을 `develop`에 병합한다.
2. `develop` 최신 상태에서 `pnpm verify:release`를 실행한다.
3. `develop -> main` 수동 merge PR을 생성한다.
4. Discord에 release PR 생성 사실을 1회 보고한다.
5. 배포 사이트에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history`를 직접 확인한다.
