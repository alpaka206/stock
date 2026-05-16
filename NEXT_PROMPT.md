1. `rg`로 깨진 한글, 제거된 자동화, 불필요한 레거시 참조를 다시 확인한다.
2. `pnpm guard:no-secrets`와 텍스트 품질 검사를 실행하고 실패를 수정한다.
3. `pnpm verify:standard`를 실행해 웹/API 변경을 검증한다.
4. 변경사항을 보안 파일 포함 여부까지 확인한 뒤 커밋하고 `develop` 대상 PR을 만든다.
5. 통합 PR 번호를 기준으로 기존 Dependabot PR을 닫거나 superseded 처리한다.
