# 현재 라운드 목표

Spring Boot 백엔드와 Next.js 프런트가 로그인, 구독 플랜, 리포트, 미디어 현지화, 실제 provider 수집 API까지 같은 계약으로 동작하도록 연결한다.

## 완료 조건

- 백엔드 provider ingest, 리포트, Perso 현지화 API가 Swagger에 노출되고 테스트를 통과했다.
- 프런트 `/workspace`에서 로그인 상태, 구독 플랜, 리포트 미리보기/발송, 미디어 자산, 현지화 작업을 서버 API로 연결했다.
- `pnpm verify:standard`, 실제 Spring API 기준 release 검증, 핵심 E2E가 통과했다.
- 백엔드 PR #8, 프런트 PR #198을 `develop`으로 squash 없이 병합했다.
- 보안 파일과 임시 로그가 커밋에 포함되지 않았는지 확인했다.
