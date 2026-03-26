# AI 주식 리서치 워크스페이스 청사진

이 저장소는 **뉴스 + 기술적 분석 + 수급 + 옵션/공매도 + 히스토리 리플레이**를 한 화면 흐름으로 묶는 웹앱을 만드는 기준 문서다.

## 1. 왜 이 구조로 시작하는가

이 프로젝트는 기능을 따로따로 추가하는 방식보다, 아래 4개 메인 화면을 먼저 고정하고 그 안에서 기능을 확장하는 방식이 더 맞다.

- `/overview` : 시황 대시보드
- `/radar` : 관심종목 + 섹터 인텔리전스
- `/stocks/[symbol]` : 종목 분석 워크스테이션
- `/history` : 과거 이벤트/변곡점 리플레이

## 2. 권장 기술 스택

### 프론트엔드

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- AG Grid Community
- TanStack Query
- next-themes
- 차트 라이브러리(금융 차트 전용 모듈)

### 백엔드

- FastAPI
- Pydantic
- Python 3.12+
- 화면 단위 endpoint
- 런타임 AI 프롬프트 파일 로딩 방식

## 3. 무료 전제에서 그리드는 어떻게 가져가는가

이 프로젝트의 `radar` 화면은 여전히 단순 table이 아니라 작업용 grid가 맞다. 다만 현재는 유료 라이선스를 쓰지 않으므로 **AG Grid Community** 기준으로 설계한다.

핵심 이유:

- AG Grid Community는 무료/오픈소스이며, 고급 Enterprise 기능이 꼭 필요하지 않을 때 적합하다.
- 정렬, 필터, 행 선택, 커스텀 셀, 상태 저장/복원 같은 핵심 grid 흐름은 Community 범위 안에서 설계할 수 있다.
- `row grouping` 과 `column menu` 는 Enterprise 문서로 표기되어 있으므로, Radar의 그룹 뷰와 컬럼 토글은 커스텀 UI로 대체한다.

무료 구현 원칙:

- 그룹 뷰: 좌측 폴더 트리 + 상단 뷰 모드 토글 + 사전 그룹화된 데이터셋
- 컬럼 토글: 커스텀 드롭다운/시트 + columnDefs 업데이트
- 상태 저장: `api.getState()` / `api.setState()` 또는 로컬 저장소 사용
- 커스텀 셀: AG Grid Cell Component 사용

보조 대안:

- 진짜 spreadsheet 느낌과 대량 데이터 렌더링이 더 중요해지면 Glide Data Grid(MIT)를 검토한다.
- 완전 무료 grouping 로직을 headless 방식으로 가져가려면 TanStack Table의 grouping / columnVisibility를 일부 화면에 한정해 사용할 수 있다.

## 4. 프론트엔드 기본 세팅을 한 번에 하는 순서

### 권장 선행 설치

- Node.js LTS
- pnpm
- Python 3.12+
- Git

### 루트 생성

```bash
mkdir stock-ai-workspace
cd stock-ai-workspace
git init
mkdir -p apps docs packages scripts
```

### Next.js 앱 생성

```bash
pnpm create next-app@latest apps/web --ts --tailwind --eslint --app --use-pnpm --import-alias "@/*" --yes
```

### 웹앱 의존성 설치

```bash
pnpm add -C apps/web   ag-grid-community ag-grid-react @ag-grid-community/locale   @tanstack/react-query   zod react-hook-form @hookform/resolvers   next-themes   clsx class-variance-authority tailwind-merge lucide-react
```

### shadcn/ui 초기화

```bash
cd apps/web
pnpm dlx shadcn@latest init -t next
pnpm add next-themes
cd ../..
```

### 자주 쓰는 shadcn 컴포넌트 추가 예시

```bash
cd apps/web
pnpm dlx shadcn@latest add button card tabs badge input select separator sheet dialog dropdown-menu table skeleton tooltip scroll-area
cd ../..
```

### 백엔드 기본 생성

```bash
mkdir -p apps/api/app
python -m venv .venv
source .venv/bin/activate   # Windows는 .venv\Scripts\activate
pip install fastapi uvicorn[standard] pydantic httpx
```

### 루트 워크스페이스 파일

루트에 아래 파일을 추가한다.

- `pnpm-workspace.yaml`
- 루트 `package.json`
- 루트 `AGENTS.md`

예시:

```yaml
packages:
  - apps/*
  - packages/*
```

## 5. 추천 루트 package.json 예시

```json
{
  "name": "stock-ai-workspace",
  "private": true,
  "packageManager": "pnpm@10",
  "scripts": {
    "dev:web": "pnpm --dir apps/web dev",
    "build:web": "pnpm --dir apps/web build",
    "lint:web": "pnpm --dir apps/web lint",
    "typecheck:web": "pnpm --dir apps/web exec tsc --noEmit"
  }
}
```

## 6. 폴더 구조

전체 폴더 구조는 `docs/architecture/page-manifest.yaml` 과 `docs/architecture/component-manifest.yaml` 을 기준으로 삼는다.
상세 구조는 해당 문서를 참고한다.

## 7. Codex에게 무엇을 어떻게 기억시키는가

Codex가 매번 네 디자인과 4페이지 IA를 다시 물어보지 않게 하려면, 지시를 채팅에 반복하는 대신 저장소 안에 **지속 문서**를 둬야 한다.

필수 파일:

- `AGENTS.md`
- `apps/web/AGENTS.md`
- `apps/api/AGENTS.md`
- `docs/design/design-memory.md`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`

즉,

- **AGENTS.md = 작업 규칙**
- **design-memory = 디자인 방향 기억**
- **page/component manifest = 구조 기억**
- **changes/adr = 변경 역사 기억**

## 8. 런타임 AI 프롬프트와 계약 파일을 어떻게 나누는가

이건 Codex용 문서와 다르다.
Codex용 지침은 `AGENTS.md` 에 두고, 실제 서비스가 LLM을 호출할 때 쓰는 prompt body는 `apps/api/prompts/` 에 둔다.

canonical runtime contract source:

- `packages/contracts/schemas/overview.schema.json`
- `packages/contracts/schemas/radar.schema.json`
- `packages/contracts/schemas/stocks.schema.json`
- `packages/contracts/schemas/history.schema.json`

prompt body 파일:

- `apps/api/prompts/common/system.rules.md`
- `apps/api/prompts/overview/system.md`
- `apps/api/prompts/radar/system.md`
- `apps/api/prompts/stock_detail/system.md`
- `apps/api/prompts/history/system.md`

호환성 복사본:

- `apps/api/prompts/*/output.schema.json`

코드에서는

1. 공통 규칙 파일 읽기
2. 페이지별 시스템 프롬프트 읽기
3. `packages/contracts/schemas/*.schema.json`에서 canonical output schema 읽기
4. 실제 데이터 payload 주입
5. 모델 응답 검증

순서로 동작시킨다.

## 9. 문서화/변경기록 원칙

- 기존 문서를 삭제하지 않는다.
- 변경 이유는 항상 남긴다.
- 큰 결정은 ADR로 남긴다.
- 작업 후 changelog를 append-only 로 추가한다.

## 10. Codex 프롬프트 순서

권장 순서는 `docs/codex/prompt-order.md` 참고.

요약 순서:

1. 저장소 부트스트랩
2. 웹앱 스캐폴딩
3. API 스캐폴딩
4. overview 구현
5. radar 구현
6. stock detail 구현
7. history 구현
8. shared contracts 정리
9. 테스트/문서/체인지로그 정리

## 11. 지금 바로 가장 먼저 할 일

1. 루트에 3개의 AGENTS.md 를 배치한다.
2. `design-memory.md` 와 `page-manifest.yaml` 을 먼저 커밋한다.
3. 그 다음 Codex에 `docs/prompts/00-레포-부트스트랩.md` 부터 순서대로 보낸다.
## 12. contract source of truth

- runtime JSON schema canonical source는 `packages/contracts/schemas/*.schema.json`
- `apps/api/prompts/*/output.schema.json`은 호환성 복사본이며 canonical source가 아니다
- prompt body는 계속 `apps/api/prompts/*/system.md`에 둔다
- web runtime type은 `packages/contracts/src/index.ts`를 기준으로 본다
- `python scripts/check_contract_parity.py`가 contracts / Pydantic / legacy prompt copy drift를 실패로 드러낸다
