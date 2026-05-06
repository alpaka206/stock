현재 라운드 목표
- PR #135까지 포함한 `develop_loop` 변경이 `develop`으로 들어갈 수 있는 상태를 만든다.
- 실패하던 Dependabot PR들을 배치 반영 또는 보류 사유와 함께 정리한다.
- 남은 차단 조건을 상태 문서에 관측 가능한 기준으로 남긴다.

완료 조건
- PR #135가 `develop_loop`에 병합되어 PR #155에 포함된다.
- PR #155(`develop_loop -> develop`)의 GitHub checks가 통과하고 auto-merge가 설정된다.
- Dependabot PR #138, #139, #140, #145, #148, #149, #150, #152, #153은 배치 반영 사실을 남기고 닫힌다.
- ESLint 10 PR #151은 lint 호환성 보류 사유를 남기고 닫힌다.
- 남은 차단 조건이 `STATE.md`와 `NEXT_PROMPT.md`에 한국어로 기록된다.
