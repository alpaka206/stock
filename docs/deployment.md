# 배포 문서

## 권장 구조

- Web: Vercel 또는 Docker 기반 Node 호스트
- Backend: `stock_BE` Spring Boot Docker 서비스
- DB: Postgres
- Cache/Queue: Redis
- 배치/자동 수집: n8n 또는 별도 worker 서비스

## 로컬 Docker Compose

이 저장소의 Compose는 프런트만 실행하고 Spring 백엔드는 외부 서비스로 둔다.

```bash
docker compose up --build
```

- Web: `http://localhost:3000`
- Backend 기본값: `http://host.docker.internal:8080`

백엔드 Docker와 DB는 `../stock_BE`에서 별도 Compose로 관리한다.

## 배포 전 체크

1. 프런트: `pnpm verify:standard`
2. 백엔드: `cd ../stock_BE && .\mvnw.cmd test`
3. Spring `/actuator/health/readiness`
4. Spring `/v3/api-docs`, `/swagger-ui.html`
5. Web `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`
6. `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`
7. 실제 provider API 키, Postgres, Redis, cookie secure 설정 확인

## GitHub 보호 규칙

- squash merge는 사용하지 않는다.
- merge 후 branch 자동 삭제는 꺼둔다.
- `main`, `develop` 브랜치는 force push와 branch deletion을 금지한다.
- `main` 병합은 PR을 통해서만 진행한다.
- `main`은 배포 트리거 브랜치이므로 여러 `develop` 변경을 묶어 사용자가 요청한 릴리스 시점에만 `develop -> main` PR을 연다.
- 프런트 PR에는 `verify`, `dependency-review`, `codeql (javascript-typescript)` 통과가 필요하다.
- Dependabot security updates, vulnerability alerts, secret scanning, push protection을 켠 상태로 유지한다.

## 남은 리스크

- Alpha Vantage 무료 플랜 quota는 운영 트래픽에 부족할 수 있다.
- 국내장 실시간성은 provider 선택에 따라 달라진다.
- 백엔드 DB migration과 프런트 계약 변경은 같은 릴리스 묶음에서 검증해야 한다.
