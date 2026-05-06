현재 라운드 목표
- #160 provider 리팩터링 PR #172 병합 이후 release 준비 상태를 정리한다.
- `develop` 기준 release 검증을 실행하고 `develop -> main` 수동 merge PR을 준비한다.
- release PR 생성 시 Discord 보고와 배포 핵심 경로 확인까지 이어간다.

완료 조건
- `STATE.md`에 PR #172 병합과 GitHub checks 성공 사실이 기록된다.
- `pnpm verify:release`가 통과한다.
- `develop -> main` PR이 생성되고 자동 병합이 설정되지 않는다.
- Discord에 release PR 생성 사실이 1회 보고된다.
