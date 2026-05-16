# 기여 가이드

## 기본 흐름

- 기준 브랜치: `develop`
- 릴리스 브랜치: `main`
- 작업 브랜치: `feat/<issue>-<slug>` 또는 `fix/<issue>-<slug>`
- PR 흐름: issue branch -> `develop`, 릴리스 시 `develop -> main`
- `main`은 배포 트리거 브랜치이므로 자주 병합하지 않고, 사용자가 요청한 릴리스 묶음 단위로만 반영합니다.

## 강제 규칙

- `main`, `develop`에 직접 커밋하지 않습니다.
- `main`, `develop`에 직접 push하지 않습니다.
- force push는 금지합니다.
- `develop -> main` PR은 릴리스 묶음이 준비됐을 때만 만들고, 사용자가 직접 최종 병합합니다.
- 커밋과 PR 제목에 `[codex]`를 붙이지 않습니다.
- squash merge는 사용하지 않습니다. 여러 커밋의 의미를 유지할 수 있도록 merge commit 또는 rebase merge만 허용합니다.
- `main` 브랜치는 보호 규칙으로 force push와 삭제가 금지되어야 하며, 필수 체크가 통과한 PR만 병합합니다.
- `develop` 브랜치도 보호 규칙으로 force push와 삭제가 금지되어야 합니다.
- merge 후 branch 자동 삭제는 사용하지 않습니다. 영구 브랜치가 release PR 병합 후 삭제될 수 있기 때문입니다.

## 제목 규칙

이슈, PR, 커밋 제목은 아래 접두사 중 하나로 시작합니다.

- `feat:`
- `fix:`
- `refactor:`
- `docs:`
- `chore:`
- `ci:`
- `test:`
- `perf:`

예:

```text
feat: 레이더 테이블 성능 개선
docs: Docker 실행 문서 정리
```

## 검증

```powershell
pnpm verify:standard
pnpm verify:release
```

상황별 부분 검증:

```powershell
pnpm lint:web
pnpm typecheck:web
pnpm build:web
python scripts/api_smoke.py
python scripts/verify_workspace.py --group api
```

## 보안

- `.env`, `.env.*`, API 키, 토큰, 웹훅 URL은 커밋하지 않습니다.
- 목데이터 또는 fallback 데이터는 사용자 화면에 `(목데이터)`로 표시합니다.
- 실제 데이터 API 오류와 누락 데이터 처리 방식을 PR에 적습니다.
