1. PR checks가 모두 통과했는지 확인하고 실패가 있으면 같은 브랜치와 같은 PR에 수정 커밋을 올린다.
2. PR이 `develop`에 병합되면 `develop`을 최신화한 뒤 이슈 #159용 새 브랜치를 만든다.
3. `/overview`, `/radar`, `/stocks/[symbol]`, `/history`의 Playwright E2E 검증을 추가한다.
4. E2E 검증 후 `pnpm verify:automation`, `pnpm verify:standard`를 다시 실행한다.
