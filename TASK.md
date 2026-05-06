현재 라운드 목표
- 이슈 #162 기준으로 한국 OpenDART 공시 흐름에 미국 SEC filings 데이터 소스를 추가한다.
- 뉴스와 캘린더에서 미국 watchlist filings가 함께 노출되도록 real/mock provider와 검증을 보강한다.
- 변경사항을 커밋하고 `develop` 대상 PR로 올린다.

완료 조건
- SEC submissions client가 watchlist CIK 매핑으로 10-K, 10-Q, 8-K 등 주요 filings를 파싱한다.
- `/news` featured feed에 SEC filings가 글로벌 공시 성격으로 병합된다.
- `/calendar` market events에 SEC filing 이벤트가 글로벌 disclosure로 병합된다.
- `pnpm test:e2e -- --project=chromium`, `pnpm verify:automation`, `pnpm verify:standard`가 통과한다.
