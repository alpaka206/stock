# 배포 문서

## 권장 토폴로지

- Web: Vercel 또는 Docker 기반 Node 런타임
- API: Docker 기반 FastAPI 런타임
- DB: Postgres
- 배치/자동 수집: 추후 n8n 또는 별도 worker 서비스

## Docker Compose

```bash
docker compose up --build
```

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- Postgres: `localhost:5432`

## 운영 후보 체크

1. `pnpm verify:standard`
2. `pnpm verify:release`
3. API `/health` 통과
4. API `/readyz?probe=config` 통과
5. Web `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA` 직접 확인
6. `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`
7. `DATABASE_URL`과 실제 provider API 키 설정

## 남은 리스크

- Alpha Vantage 무료 플랜 quota는 운영 트래픽에 부족할 수 있다.
- 국내장 실시간성은 provider 선택에 따라 크게 달라진다.
- 별도 백엔드 저장소로 분리하면 DB migration과 계약 배포 순서를 추가로 관리해야 한다.
