현재 라운드 목표
- #175 종목 상세 화면의 API 버전 차이 fallback을 보강한다.
- release PR #174가 최신 `develop`을 따라가도록 fix PR을 병합한다.
- release 검증과 핵심 화면 브라우저 확인 결과를 문서에 남긴다.

완료 조건
- `/stocks/NVDA`가 신규 stock detail 필드가 없는 API 응답에서도 깨지지 않는다.
- 로컬 develop 브라우저 확인에서 `/overview`, `/radar`, `/stocks/NVDA`, `/history`가 모두 200으로 열린다.
- `pnpm verify:standard`가 통과한다.
- #175 PR이 `develop`에 병합되고 release PR #174가 갱신된다.
