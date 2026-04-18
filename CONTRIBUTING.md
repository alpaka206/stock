# 기여 가이드

`stock` 저장소는 공개 협업을 허용하지만, 브랜치 보호와 릴리스 규칙이 강합니다.

## 어디에 남겨야 하는가

- 질문/아이디어/방향 논의: GitHub Discussions
- 실제 작업 제안: GitHub Issue
- 보안 취약점: 공개 이슈 금지, [보안 정책](.github/SECURITY.md) 사용

## 브랜치 흐름

- 작업 기준 브랜치: `develop_loop`
- 작업 브랜치: `issue/<number>-<slug>`
- 안정 브랜치: `develop`
- 릴리스 브랜치: `main`

## 강제 규칙

- `main`, `develop` 직접 push 금지
- `main`, `develop` 강제 push 금지
- `develop`으로 들어가는 PR은 코드 오너 승인 필수
- `main`은 `develop -> main` PR만 허용
- `main` 대상 PR 작성자는 `alpaka206`만 허용

## 제목 규칙

이슈/PR 제목은 작업 성격이 바로 보이도록 아래 접두어를 사용합니다.

- `feat:`
- `fix:`
- `refactor:`
- `docs:`
- `chore:`
- `ci:`
- `test:`
- `perf:`

`auto-generated`, `자동 생성`, 의미 없는 범용 제목은 사용하지 않습니다.

## 로컬 검증

```powershell
pnpm verify:standard
pnpm verify:automation
```

상황에 따라 아래도 사용합니다.

```powershell
pnpm lint:web
pnpm build:web
python scripts/api_smoke.py
python scripts/verify_workspace.py --group api
```

## 문서

- 상세 설계와 운영 문서 정본: `docs/`
- 빠른 입문용 링크 모음: GitHub Wiki
