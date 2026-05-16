# 현재 상태

## 현재 사실

- 기준 브랜치는 `develop`이다.
- 프런트와 백엔드 모두 로컬 기준 브랜치는 `develop`이다.
- 백엔드 관련 issue는 `alpaka206/stock_BE#7`이고 PR #8이 merge commit `ab78940`으로 `develop`에 반영됐다.
- 프런트 관련 issue는 `alpaka206/stock#197`이고 PR #198이 merge commit `903ab1f`로 `develop`에 반영됐다.
- 최종 인계 문서는 문서 정리 issue 흐름으로 최신화했다.
- 백엔드는 Spring Boot를 기준으로 진행한다. FastAPI 런타임과 무한 자동화 루프는 제품 경로에서 제외했다.
- 사용자에게 보여야 하는 핵심 데이터는 프런트가 외부 provider를 직접 호출하지 않고 백엔드 API와 BFF를 통해 조회한다.
- 인증은 백엔드가 `HttpOnly` access/refresh cookie를 발급하고, 프런트 BFF가 브라우저 쿠키와 CSRF 헤더를 함께 전달하는 구조다.
- 구독별 접근 제한은 아직 강제하지 않는다. 테스트와 화면 검증을 위해 플랜 비교와 사용량 안내만 표시한다.
- 실제 provider key, SMTP, Perso key가 없을 때는 목 데이터를 생성하지 않고 설정 필요 상태를 반환한다.

## 최근 검증 결과

- 백엔드 `.\mvnw.cmd test` 통과.
- 프런트 `pnpm verify:standard` 통과.
- Spring Boot test/H2 서버를 기준으로 `STOCK_API_BASE_URL=http://localhost:8080`, `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`를 지정해 `pnpm verify:release` 통과.
- 로컬 FE/BE 서버를 기준으로 `E2E_SKIP_WEB_SERVER=true`, `E2E_BASE_URL=http://localhost:3000`를 지정해 `pnpm test:e2e` 통과.
- `/workspace` 화면을 Playwright screenshot으로 확인했고 텍스트 겹침과 주요 레이아웃 깨짐은 발견하지 못했다.
- 보안 파일은 읽거나 커밋하지 않았고, 새 환경 변수는 `.env.example`과 문서에 placeholder로만 정리했다.
- GitHub PR checks는 백엔드, 프런트, 문서 정리 PR 모두 통과했고 squash 없이 merge commit 방식으로 병합했다.

## 남은 리스크

- Alpha Vantage, OpenDART, SEC, Perso, SMTP는 실제 운영 키와 계정을 연결한 뒤 별도 smoke test가 필요하다.
- Perso API의 실제 응답 필드는 계정/상품 설정에 따라 달라질 수 있어 운영 연결 후 mapper 보정이 필요할 수 있다.
- 이메일 발송은 `REPORT_EMAIL_SENDING_ENABLED=true`와 SMTP 설정이 들어가기 전까지 DB에 `READY` 상태로 저장된다.
- 구독별 기능 제한, 결제, Google OAuth 운영 client 설정은 다음 단계에서 붙여야 한다.
- develop에서 main으로 자주 올리지 않는다. release PR은 생성하되 사용자가 직접 병합하는 정책을 유지한다.

## 다음 우선순위

1. 운영 키 연결 후 provider ingest, Perso submit/sync, 이메일 발송 smoke test를 수행한다.
2. Google OAuth 운영 client, 결제, 구독별 기능 제한을 단계적으로 연결한다.
3. develop 누적 변경이 안정화되면 `develop -> main` release PR을 생성하고 병합은 사용자가 직접 진행한다.
