# 현재 상태

## 현재 사실

- 기준 브랜치: `develop`
- 현재 프런트 브랜치: `refactor/189-use-spring-backend`
- 관련 이슈: #189 `UI/UX 리디자인 및 자동화 제거`
- `main`은 배포 트리거 브랜치이므로 자주 병합하지 않는다. `develop`에 변경을 모은 뒤 릴리스 묶음 단위로만 `develop -> main` PR을 연다.
- squash merge는 사용하지 않는다.
- 무한 루프형 자동화와 외부 채팅 브리지 자동화 잔여 참조는 제거됐다.
- 운영 백엔드는 별도 저장소 `alpaka206/stock_BE`의 Spring Boot API로 진행한다.
- 프런트 저장소에서 `apps/api` FastAPI 앱, API smoke, Python provider test, contract parity script를 제거했다.
- 프런트 Docker Compose는 Next.js web만 실행하고 `STOCK_API_BASE_URL`로 Spring 백엔드에 연결한다.
- 백엔드 PR #6은 checks 통과 후 merge commit `047001f`로 `develop`에 반영됐다.
- 백엔드 PR #6에는 화면 계약/저장 API, CSRF 조회 API, Swagger/OpenAPI, Google OAuth 이후 `HttpOnly` access/refresh cookie 세션 구조가 포함됐다.
- refresh token은 백엔드 DB에 원문 저장 없이 SHA-256 hash로 저장하고, `/auth/refresh`에서 회전한다.
- 접근 제한은 아직 강제하지 않는다. 테스트 편의를 위해 API는 열어두고 세션 계약만 준비한다.

## 최근 검증 결과

- 백엔드 `.\mvnw.cmd test` 통과. 총 5개 테스트 성공.
- 백엔드 `git diff --check` 통과. CRLF 안내만 표시됨.
- 백엔드 비밀값 검색: 실제 키 없음. `.env.example` placeholder와 Maven wrapper 기본 변수만 탐지.
- 프런트 FastAPI 잔여 참조 스캔에서 현재 문서/스크립트 경로는 Spring Boot 기준으로 정리됨.
- 프런트 `pnpm verify:standard` 통과. 텍스트 품질, 비밀값 가드, lint, typecheck, build가 모두 성공했다.

## 남은 리스크

- 프런트 PR #196은 GitHub Actions 완료를 기다려야 한다.
- 실제 데이터 API 키가 없는 환경에서는 fallback 데이터가 보이며, 사용자 화면에는 `(목데이터)`로 표시해야 한다.
- 외부 provider 수집 결과를 백엔드 DB에 저장하는 ingest 작업은 아직 남아 있다.
- 로그인 UI와 접근 제한은 아직 붙이지 않았다.

## 다음 우선순위

1. 프런트 타입체크/빌드 실패를 고친 뒤 `pnpm verify:standard`를 통과시킨다.
2. 프런트 PR #196 checks 완료 후 develop에 merge commit 방식으로 반영한다.
3. develop branch protection required checks에서 삭제된 Python CodeQL 체크가 남아 있으면 제거한다.
4. 백엔드 ingest worker와 실제 provider 저장 흐름을 추가한다.
5. 로그인 UI, 구독 요금제, 리포트 이메일 발송 구조를 접근 제한 없이 화면/저장 API부터 붙인다.
