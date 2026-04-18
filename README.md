# Stock Workspace

Stock Workspace는 국장과 미장을 함께 보는 주식 리서치 워크스페이스 모노레포입니다. 시장 개요, 관심 종목, 종목 상세, 히스토리, 뉴스, 이벤트 캘린더를 하나의 흐름으로 연결하는 것을 목표로 합니다.

## 커뮤니티

- Discussions: [https://github.com/alpaka206/stock/discussions](https://github.com/alpaka206/stock/discussions)
- Wiki: [https://github.com/alpaka206/stock/wiki](https://github.com/alpaka206/stock/wiki)
- 기여 가이드: [CONTRIBUTING.md](CONTRIBUTING.md)
- 보안 정책: [.github/SECURITY.md](.github/SECURITY.md)
- 라이선스: [LICENSE](LICENSE)

## 제품 구조

주요 라우트:
1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

보조 라우트:
- `/news`
- `/calendar`

`watchlist`는 별도 최상위 라우트 대신 `/radar` 내부 기능으로 유지합니다.

## 저장소 구조

- `apps/web`: Next.js 프론트엔드
- `apps/api`: FastAPI 백엔드
- `packages/contracts`: 공통 스키마와 타입
- `docs`: 아키텍처, 배포, 설계, 프롬프트, 운영 문서
- `scripts`: 검증 및 자동화 스크립트
- `.omx`: 레포 로컬 자율 실행 상태와 로그

## 로컬 개발

웹:

```powershell
pnpm install
pnpm dev:web
```

API:

```powershell
cd apps/api
python -m pip install .
python -m uvicorn app.main:app --reload
```

## 검증

기본:

```powershell
pnpm verify:standard
pnpm verify:automation
```

집중 검증:

```powershell
pnpm verify:web
pnpm verify:api
python scripts/api_smoke.py
```

## 런타임 메모

- 웹은 `STOCK_API_BASE_URL` 또는 라우트별 env를 통해 별도 API 대상을 바라봅니다.
- API 요약 생성은 `OpenAI -> Gemini -> deterministic fallback` 순서로 동작할 수 있습니다.
- `.env.discord`는 로컬 전용이며 커밋하지 않습니다.

## Codex / Ralph Loop

- 프로젝트별 Ralph 설정: `.ralph-loop.yml`
- 로컬 Codex 설정: `.codex/`
- 로컬 브랜치 안전 가드: `.githooks/`
- 런타임 해석기: `scripts/ralph_runtime.py`
- 다른 저장소 부트스트랩: `powershell -ExecutionPolicy Bypass -File scripts/ralph-init.ps1 -TargetRepo C:\path\to\repo`
- Codex Ralph 실행: `powershell -ExecutionPolicy Bypass -File scripts/ralph-run.ps1`
- Discord 브리지 실행: `powershell -ExecutionPolicy Bypass -File scripts/run-discord-bridge.ps1`
- 자율 루프 실행: `powershell -ExecutionPolicy Bypass -File scripts/omx-loop.ps1 -InfiniteMode`

Discord 제어 명령:
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
- `develop`은 코드 오너 승인 없이는 머지할 수 없습니다.
- `main`은 `develop -> main` PR만 허용합니다.
- `main` 대상 릴리스 PR 작성자는 `alpaka206`만 허용합니다.
- `develop`, `main` 강제 푸시는 금지합니다.

## 재사용 구조

- `.ralph-loop.yml`: 목표, 완료 조건, Discord 라우팅, 브랜치 정책, 런타임 포트
- `.codex/`: Codex hooks, rules, agents
- `.githooks/`: 로컬 git 안전 가드
- `scripts/omx_autonomous_loop.py`: 메인 루프 엔진
- `scripts/ralph_runtime.py`: 저장소별 런타임 해석기
- `scripts/ralph-init.ps1`: 다른 저장소용 1회 부트스트랩
- `omx_discord_bridge/`: Discord 브리지
- `plugins/stock-omx-loop/`: 레포 로컬 skill/plugin 번들
