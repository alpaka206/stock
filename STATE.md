현재 사실
- PR #165, #166, #167, #168, #169, #170, #171, #172, #173, #176이 모두 `develop`에 병합됐다.
- release PR #174 `release: develop 변경사항 main 반영`은 `develop -> main`으로 열려 있고 auto-merge는 설정하지 않았다.
- release PR #174의 head는 최신 `develop` 커밋 `afe3fe2`를 포함한다.
- release PR #174 생성 사실은 Discord에 1회 보고했고 브리지 응답은 204였다.
- 완료된 이슈 #175는 닫았다. 열린 작업 이슈는 #160, #177과 장기 상위 이슈 #131이다.
- Dependabot PR은 현재 열린 항목이 없으며 과거 실패 PR들은 닫힌 상태다.

최근 검증 결과
- PR #176 GitHub checks: verify, dependency-review, CodeQL, Vercel 모두 성공했고 `develop`에 병합됐다.
- release PR #174 최신화 후 GitHub checks: verify, dependency-review, CodeQL, release-guard, Vercel 모두 성공했다.
- `pnpm verify:release` 재실행 통과. remote API `/readyz?probe=remote`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`, `/instruments/search?q=nvda`가 200 JSON 응답을 반환했다.
- #175 수정 후 develop 로컬 브라우저 확인에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history`가 모두 200으로 열렸고 콘솔 오류가 없었다.
- 배포 프런트 `https://stock-radar-board.vercel.app` 직접 확인에서 현재 main 기준 `/stocks/NVDA`, `/history`는 열렸고 `/overview`, `/radar`는 500이었다.

남은 리스크
- production 프런트의 `/overview`, `/radar` 500은 release PR #174가 main에 수동 merge되어 새 배포가 끝난 뒤 다시 확인해야 한다.
- main merge는 `RELEASE_TO_MAIN_POLICY=pr-only-manual-merge` 때문에 사용자가 직접 수행해야 한다.
- #160의 provider 분리는 radar/stock/history 중심으로 완료됐고, overview/news/calendar builder 경계는 아직 더 분리할 여지가 있다.
- 조건 감지 알림은 `/radar` 표시까지만 연결됐고 사용자별 임계값 저장, 알림 히스토리, Discord/브라우저 알림 전송은 아직 없다.

다음 우선순위
- 사용자가 release PR #174를 main에 수동 merge한다.
- Vercel production 배포가 끝난 뒤 `https://stock-radar-board.vercel.app/overview`, `/radar`, `/stocks/NVDA`, `/history`를 다시 확인한다.
- production 확인 결과를 문서와 저널에 기록한다.
- 이후 #160 후속으로 overview/news/calendar provider builder 경계를 더 분리한다.
