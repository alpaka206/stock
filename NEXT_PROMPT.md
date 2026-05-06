1. PR #155(`develop_loop -> develop`) 리뷰 요구 조건을 충족하고 auto-merge 결과를 확인한다.
2. PR #155가 병합되면 `origin/develop`을 fetch한 뒤 `pnpm verify:automation`, `pnpm verify:standard`, release 검증을 다시 실행한다.
3. ESLint 10은 `eslint-plugin-react` 호환성 확인 전까지 다시 열지 않는다.
4. `develop -> main` release PR을 만들 경우 수동 merge 정책을 지키고 Discord에 보고한다.
