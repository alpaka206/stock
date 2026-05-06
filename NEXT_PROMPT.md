1. 이슈 브랜치를 push하고 `develop_loop` 대상 PR을 생성한다.
2. PR 체크가 끝나면 실패 여부를 확인하고 필요한 수정은 같은 브랜치에 반영한다.
3. Dependabot PR들은 배치 반영 또는 ESLint 10 보류 사유를 코멘트한 뒤 정리한다.
4. `develop_loop -> develop` PR 생성 또는 기존 흐름 정리까지 진행한다.
5. `develop` 반영 후 release PR 필요 여부를 확인한다.
