# Stock Workspace

`stock`는 국장과 미장을 함께 보는 주식 분석 워크스페이스 모노레포입니다. 시장 개요, 스크리너, 종목 상세, 뉴스, 캘린더, 히스토리를 하나의 제품 흐름으로 연결하는 것을 목표로 합니다.

## 커뮤니티

- Discussions: [https://github.com/alpaka206/stock/discussions](https://github.com/alpaka206/stock/discussions)
- Wiki: [https://github.com/alpaka206/stock/wiki](https://github.com/alpaka206/stock/wiki)
- 기여 가이드: [CONTRIBUTING.md](CONTRIBUTING.md)
- 보안 정책: [.github/SECURITY.md](.github/SECURITY.md)
- 라이선스: [LICENSE](LICENSE)

## 제품 구조

주요 라우트
1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

보조 라우트
- `/news`
- `/calendar`

`watchlist`는 별도 최상위 라우트 대신 `/radar` 내부 기능으로 유지합니다.

## 저장소 구조

- `apps/web`: Next.js 프런트엔드
- `apps/api`: FastAPI 백엔드
- `packages/contracts`: 공통 스키마와 타입
- `docs`: 아키텍처, 운영, 배포, 프롬프트, 위키 원본 문서
- `scripts`: 검증과 자동화 스크립트
- `.omx`: 로컬 런타임 상태와 로그

## 로컬 실행

web

```powershell
pnpm install
pnpm dev:web
```

api

```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## 검증

기본 검증

```powershell
pnpm verify:standard
pnpm verify:automation
```

선택 검증

```powershell
pnpm verify:web
pnpm verify:api
python scripts/api_smoke.py
```

## 배포 주소

- 현재 배포된 stock 사이트: [https://stock-radar-board.vercel.app](https://stock-radar-board.vercel.app)
- 대표 진입 화면: [https://stock-radar-board.vercel.app/overview](https://stock-radar-board.vercel.app/overview)

## Codex / Ralph Loop

- 프로젝트별 Ralph 설정: `.ralph-loop.yml`
- 로컬 Codex 설정: `.codex/`
- 로컬 브랜치 안전 가드: `.githooks/`
- 공통 런타임 해석기: `scripts/ralph_runtime.py`
- 다른 저장소 부트스트랩: `powershell -ExecutionPolicy Bypass -File scripts/ralph-init.ps1 -TargetRepo C:\path\to\repo`
- Codex Ralph 실행: `powershell -ExecutionPolicy Bypass -File scripts/ralph-run.ps1`
- Discord 브리지 실행: `powershell -ExecutionPolicy Bypass -File scripts/run-discord-bridge.ps1`
- 자율 루프 실행: `powershell -ExecutionPolicy Bypass -File scripts/omx-loop.ps1 -InfiniteMode`

Discord 제어 명령

- `/ralph status`
- `/ralph pause`
- `/ralph resume`
- `/ralph stop`
- `/ralph nudge <message>`
- `/ralph goal <message>`
- `/ralph done <message>`
- `/ralph logs`
- `/ralph pr`

## GitHub 정책

- `develop`, `main`은 보호 브랜치입니다.
- `main`은 `develop -> main` PR만 허용합니다.
- `main` 대상 PR 작성자는 `alpaka206`만 허용합니다.
- `develop`, `main`은 직접 push와 force push를 금지합니다.
- `develop_loop -> develop`, `develop -> main` 같은 장수 브랜치 승격은 조상 관계를 보존해야 하므로 `merge` 전략을 사용합니다.
- `issue/<number>-<slug> -> develop_loop`는 작은 작업 단위를 빠르게 정리하기 위해 `squash` 전략을 유지합니다.

## 작업 흐름

1. `develop_loop`에서 이슈 브랜치 `issue/<number>-<slug>`를 만든다.
2. 이슈 브랜치에서 작업 후 `develop_loop`로 PR을 연다.
3. `develop_loop -> develop` 승격 PR을 연다.
4. 최종 릴리스는 반드시 `develop -> main` PR로 올린다.

장수 브랜치 승격을 `squash`로 처리하면 다음 릴리스에서 조상 관계가 끊겨 `develop -> main`이 다시 더러워질 수 있습니다. 그래서 `develop_loop -> develop`, `develop -> main`은 `merge` 기준으로 운영합니다.
