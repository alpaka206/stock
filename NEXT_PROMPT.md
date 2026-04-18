1. 이슈 #134 기준 새 issue 브랜치를 만들어 `apps/web/lib/server/research-api.ts` 의 `[::1]` 로컬 판정 보완을 최소 수정으로 구현한다.
2. `[::1]` base URL 을 재현하는 회귀 테스트 1건을 추가하고 관련 검증만 다시 통과시킨다.
3. PR #132 의 CI와 auto-merge 결과를 확인한다.
4. 실제 배포 프런트 URL을 찾을 수 있으면 `/overview`, `/radar`, `/stocks/NVDA`, `/history` 를 다시 직접 확인한다.
