# 배포 문서

## 권장 구조

- Web: Vercel 또는 Docker 기반 Node 호스트
- API: Docker 기반 FastAPI 호스트
- DB: Postgres
- 배치/자동 수집: 추후 n8n 또는 별도 worker 서비스

## Docker Compose

```bash
docker compose up --build
```

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- Postgres: `localhost:5432`

## 배포 전 체크

1. `pnpm verify:standard`
2. `pnpm test:e2e`
3. `pnpm audit --audit-level low`
4. API `/health`
5. API `/readyz?probe=config`
6. Web `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`
7. `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`
8. `DATABASE_URL`과 실제 provider API 키 설정

## GitHub 보호 규칙

- squash merge는 사용하지 않는다.
- `main` 브랜치는 force push와 branch deletion을 금지한다.
- `main` 병합은 PR을 통해서만 진행한다.
- `main` PR에는 `verify`, `release-guard`, `dependency-review`, `codeql (javascript-typescript)`, `codeql (python)` 통과가 필요하다.
- Dependabot security updates, vulnerability alerts, secret scanning, push protection을 켠 상태로 유지한다.

## 남은 리스크

- Alpha Vantage 무료 플랜 quota는 운영 트래픽에 부족할 수 있다.
- 국내장 실시간성은 provider 선택에 따라 달라진다.
- 백엔드 저장소를 별도로 분리하면 DB migration과 API 계약 배포 순서를 별도 문서로 관리해야 한다.
