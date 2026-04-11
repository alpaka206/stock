# CHANGELOG (Append Only)

## 2026-03-15 13:00 KST
### 무엇을
- 4개 메인 페이지 중심 IA를 정의했다.
- 루트, 웹, API의 `AGENTS.md` 초안을 추가했다.
- Codex 프롬프트 순서 문서를 추가했다.
- 페이지 manifest, 컴포넌트 manifest, 디자인 메모리를 추가했다.

### 왜
- 사용자가 매번 같은 구조를 다시 설명하지 않아도 Codex가 지속적으로 참조할 수 있어야 했다.
- 이후 구조 변경과 의사결정의 배경을 추적 가능하게 만들 필요가 있었다.

### 영향 범위
- 저장소 공통 작업 방식
- 문서 우선 개발 흐름

## 2026-03-15 18:40 KST
### 무엇을
- 그리드 전략을 AG Grid Community 기준으로 명확히 정리했다.
- Enterprise 전용 기능 전제를 제거하고 무료 범위 대체 UX 원칙을 문서화했다.
- 관련 README, AGENTS, manifest, ADR-0003을 갱신했다.

### 왜
- 초기 단계에서 유료 라이선스 비용을 전제로 설계하지 않기로 결정했기 때문이다.

### 영향 범위
- `/radar` grid 구현 방식
- 컬럼 숨김과 그룹 뷰 UX
- 이후 프롬프트와 문서의 기본 가정

## 2026-03-16 09:40 KST
### 무엇을
- `apps/web`에 공통 shell, theme/query provider, AG Grid 공통 래퍼, feature 폴더, 개발용 fixture, 메인 4개 화면 스캐폴드를 추가했다.

### 왜
- 금융 리서치 워크스페이스의 공통 UX 골격과 mock 데이터 흐름을 먼저 고정해야 이후 API 연동과 페이지 구현이 흔들리지 않기 때문이다.

### 어떻게
- App Router route를 thin wrapper로 유지하고 `features/*`, `components/shell`, `components/providers`, `dev/fixtures`, `lib/tokens` 구조로 분리했다.
- AG Grid Community 한국어 locale과 다크모드 중심 shell을 구성했다.

### 영향 범위
- `apps/web` 전체 레이아웃
- 메인 4개 화면 기본 UX
- AG Grid 사용 방식

## 2026-03-17 00:35 KST
### 무엇을
- `apps/api`에 FastAPI 진입점, 화면 단위 router, Pydantic 응답 모델, prompt loader, JSON schema validator, mock/real provider 분리 구조를 추가했다.

### 왜
- 메인 4개 화면을 API 단위에서 독립적으로 확장하고, 프롬프트 로딩과 응답 검증 흐름을 먼저 고정해야 이후 실제 데이터와 LLM 연동이 흔들리지 않기 때문이다.

### 어떻게
- `/overview`, `/radar`, `/stocks/{symbol}`, `/history` router를 등록하고 `app/services/prompt_loader.py`, `app/services/schema_validator.py`, `app/services/providers/*` 구조를 만들었다.
- mock provider로 즉시 응답 가능한 개발 흐름을 먼저 확보했다.

### 영향 범위
- `apps/api` 전체 구조
- 프롬프트 파일 로딩 방식
- 응답 schema 관리 방식

## 2026-03-17 02:10 KST
### 무엇을
- `apps/api` real provider에 Alpha Vantage 실데이터와 OpenAI structured output 호출을 연결했다.
- 페이지별 output schema와 `sourceRefs`, `missingData`, `confidence` 계약을 강화했다.

### 왜
- 프론트 페이지를 실제 API 계약 기준으로 붙이기 전에 데이터 수집, 요약, 출처 추적, 누락 데이터 처리 방식을 먼저 고정해야 했기 때문이다.

### 어떻게
- `app/services/clients/*`에 Alpha Vantage와 OpenAI client를 추가하고 `app/services/providers/real.py`에 페이지별 fact builder를 구현했다.
- prompt schema, `.env.example`, README, ADR-0005를 함께 갱신했다.

### 영향 범위
- `apps/api` 데이터 연동 방식
- OpenAI 응답 구조
- 프론트엔드 서버 상태 계약

## 2026-03-18 10:20 KST
### 무엇을
- `apps/web`의 `/overview` 화면을 지수 스트립, AI 시황 요약 카드, 시장 히트맵, 뉴스 패널, 섹터 강도 패널, 리스크 배너 구조로 재구성했다.
- overview feature 내부에 API 우선 + fixture fallback 로더를 추가하고, API 응답을 화면 전용 모델로 변환하는 어댑터를 넣었다.
- overview 관련 manifest와 design memory를 현재 화면 구조에 맞게 갱신했다.

### 왜
- overview만 봐도 오늘 시장의 방향을 10초 안에 읽고 다음 화면으로 자연스럽게 이동할 수 있어야 했기 때문이다.
- API가 준비된 값은 우선 사용하되, 아직 계약이 없는 값 때문에 화면이 깨지지 않도록 fallback 구조가 필요했다.

### 어떻게
- `features/overview/components/*`로 overview 전용 패널을 분리해 `page.tsx`와 route 파일은 얇게 유지했다.
- `getOverviewSnapshot()`에서 `STOCK_API_BASE_URL` 또는 `OVERVIEW_API_URL`이 있으면 `/overview` endpoint를 읽고, 실패하면 로컬 fixture를 반환하도록 구성했다.
- 각 카드에 `/radar`, `/stocks/[symbol]`, `/history`로 이어지는 CTA를 붙였다.

### 영향 범위
- `apps/web/app/overview/page.tsx`
- `apps/web/features/overview/*`
- `apps/web/lib/research/types.ts`
- `apps/web/dev/fixtures/overview.ts`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`

## 2026-03-20 16:20 KST
### 무엇을
- `/overview` live API 모드에서 broad sector가 잘못된 종목 상세 페이지로 이동하던 fallback을 제거하고, 매핑되지 않은 섹터는 `radar`로 연결되게 수정했다.
- API가 내려주지 않은 섹터 변화율을 UI에서 추정해 표시하던 로직을 제거했다.
- overview benchmark snapshot에서 미국 10년물 금리의 전일 대비 변화를 실제 시계열 기준으로 계산하도록 수정했다.

### 왜
- 실데이터가 있을 때 임의 종목이나 추정 수치를 보여주면 overview 화면 안에서 데이터 출처가 서로 충돌하게 되기 때문이다.
- 금리 변화를 0으로 고정하면 live `/overview`의 핵심 신호 하나를 지속적으로 잘못 보여주게 된다.

### 어떻게
- sector navigation을 종목 매핑이 있는 경우에만 `/stocks/[symbol]`로 보내고, 그렇지 않으면 `/radar`로 보내도록 조정했다.
- `sectorStrength`와 heatmap은 API가 `changePercent`를 제공할 때만 변화율을 렌더하도록 바꿨다.
- `AlphaVantageClient.get_treasury_yield()`에서 최근 2개 datapoint를 사용해 변화율을 계산하고 real provider snapshot에 반영했다.

### 영향 범위
- `apps/web/features/overview/lib/get-overview-snapshot.ts`
- `apps/web/features/overview/components/sector-strength-panel.tsx`
- `apps/web/features/overview/components/market-heatmap.tsx`
- `apps/web/lib/research/types.ts`
- `apps/api/app/services/clients/alpha_vantage.py`
- `apps/api/app/services/providers/real.py`

## 2026-03-20 17:05 KST
### 무엇을
- `/overview` news panel이 live API 기사 본문을 `impact` 기반의 고정 문장으로 바꾸지 않도록 수정하고, source 기반 summary만 표시하게 했다.
- overview API 계약에 `notableNews.summary`와 optional `sectorStrength.changePercent`를 추가하고 mock/real provider에 반영했다.
- live API payload 일부가 비어 있을 때 section 단위로 fixture를 다시 섞지 않도록 overview adapter와 빈 상태 UI를 정리했다.
- mixed deployment에서 `benchmarkSnapshot`이 아직 없는 구버전 API도 지수 스트립이 fixture fallback으로 유지되도록 보강했다.

### 왜
- 뉴스와 섹터 변화율을 출처 없이 만들어내면 리서치 화면의 정확도가 떨어지고 저장소 원칙에도 어긋나기 때문이다.
- 부분 배포 또는 계약 이행 중인 API와 연결될 때도 overview가 모순된 개발용 데이터로 채워지지 않아야 한다.

### 어떻게
- web adapter가 기사 요약을 source payload에서 그대로 사용하고, 요약이 없으면 본문을 생략하도록 바꿨다.
- real provider가 LLM 결과를 그대로 노출하지 않고 news summary와 sector changePercent를 source fact 기준으로 후처리하도록 했다.
- summary driver, news, heatmap, sector, risk 카드에 live empty-state를 추가하고 fixture는 mock payload 또는 전체 fallback에만 사용하도록 조정했다.

### 영향 범위
- `apps/web/features/overview/lib/get-overview-snapshot.ts`
- `apps/web/features/overview/components/ai-market-summary-card.tsx`
- `apps/web/features/overview/components/news-panel.tsx`
- `apps/web/features/overview/components/market-heatmap.tsx`
- `apps/web/features/overview/components/sector-strength-panel.tsx`
- `apps/web/features/overview/components/risk-banner.tsx`
- `apps/api/app/schemas/overview.py`
- `apps/api/app/services/providers/mock.py`
- `apps/api/app/services/providers/real.py`
- `apps/api/prompts/overview/output.schema.json`
- `apps/api/prompts/overview/system.md`

## 2026-03-20 17:20 KST
### 무엇을
- `/overview` index strip이 live API에서 `benchmarkSnapshot: []`를 받는 경우에도 fixture fallback을 타도록 수정했다.

### 왜
- mixed deployment나 부분 배포 상태에서 benchmark snapshot만 비어 있어도 상단 지수 스트립이 빈 상태로 무너지는 것은 `API 우선 + fallback` 정책과 맞지 않기 때문이다.

### 어떻게
- `buildIndexItems()`에서 `benchmarkSnapshot`이 `undefined`이거나 빈 배열이면 모두 fixture indices를 반환하도록 분기를 조정했다.

### 영향 범위
- `apps/web/features/overview/lib/get-overview-snapshot.ts`

## 2026-03-21 12:40 KST
### 무엇을
- `apps/web`의 `/radar`, `/stocks/[symbol]`, `/history`를 실제 작업 화면 수준으로 구현했다.
- radar에 폴더 트리, 태그/검색, AG Grid 기반 flat/sector view, 컬럼 토글, 정렬, 저장된 view preset, 우측 섹터 컨텍스트 패널을 추가했다.
- stock detail에 종목 검색, 대형 가격 차트, 이벤트 마커, 6개 이상 규칙/지표 토글, preset 저장, 점수/수급/공매도·옵션/이슈 탭을 추가했다.
- history에 종목 검색, range/from/to 필터, 차트-타임라인 동기화, 이전/다음 이벤트 이동, 급등/급락 이유 카드, 중복 지표 설명 카드를 추가했다.
- web loader를 `API 우선 + fixture fallback` 구조로 정리하고, URL 상태와 localStorage preset 훅을 공통화했다.
- `apps/api`의 radar/stocks/history schema, prompt schema, provider 응답 구조를 화면 구동 가능한 계약으로 확장했다.

### 왜
- overview 이후 실제 리서치 흐름을 이어받는 핵심 작업 화면 세 개가 필요했다.
- AG Grid와 차트를 중심으로 한 워크스페이스 UX를 먼저 고정해야 이후 서버 연동과 고도화가 쉬워진다.
- 숫자·시계열·정렬 가능한 값은 provider가 결정론적으로 만들고, LLM은 요약 문장에만 집중하도록 역할을 분리할 필요가 있었다.

### 어떻게
- route 파일은 thin wrapper로 유지하고, 각 화면 로직은 `features/radar`, `features/stocks`, `features/history` 내부로 분리했다.
- `useUrlState`, `useStoredState`, `useStoredPresets`, `useRecentSymbols`를 추가해 URL 공유 상태와 사용자 저장 상태를 분리했다.
- `ResearchLineChart`를 확장해 active point, marker, guide, highlight range, point selection callback을 지원하게 했다.
- `fetchResearchApiJson()` 기반 route별 loader를 만들고, `STOCK_API_BASE_URL` 또는 route-specific env override를 우선 사용한 뒤 실패 시 fixture로 fallback 하도록 구현했다.
- FastAPI는 `/history` query param을 확장하고, radar/stocks/history mock/real provider가 같은 계약을 반환하도록 맞췄다.

### 영향 범위
- `apps/web/app/history/page.tsx`
- `apps/web/app/stocks/[symbol]/page.tsx`
- `apps/web/components/research/instrument-search.tsx`
- `apps/web/dev/fixtures/history.ts`
- `apps/web/dev/fixtures/instruments.ts`
- `apps/web/dev/fixtures/radar.ts`
- `apps/web/dev/fixtures/stock-detail.ts`
- `apps/web/features/chart/components/research-line-chart.tsx`
- `apps/web/features/history/*`
- `apps/web/features/radar/*`
- `apps/web/features/stocks/*`
- `apps/web/lib/client/*`
- `apps/web/lib/server/research-api.ts`
- `apps/web/lib/research/types.ts`
- `apps/api/app/routers/history.py`
- `apps/api/app/schemas/radar.py`
- `apps/api/app/schemas/stocks.py`
- `apps/api/app/schemas/history.py`
- `apps/api/app/services/providers/base.py`
- `apps/api/app/services/providers/mock.py`
- `apps/api/app/services/providers/real.py`
- `apps/api/prompts/radar/*`
- `apps/api/prompts/stock_detail/*`
- `apps/api/prompts/history/*`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`

## 2026-03-21 14:10 KST
### 무엇을
- `/history`에서 canned range로 전환할 때 기존 `from` / `to` query가 남아 커스텀 기간이 계속 우선되던 흐름을 수정했다.
- real history provider가 선택 범위 밖 뉴스 날짜를 timeline에 그대로 올리던 문제를 수정하고, 뉴스 이벤트 날짜를 현재 priceSeries의 캔들 날짜에 정렬했다.
- radar preset 저장 시 실제 sector filter가 없는데도 선택 row의 섹터를 저장해 재적용 시 단일 섹터 grid로 좁혀지던 문제를 수정했다.
- stock workstation에서 rule preset과 chart guide id가 어긋나 overlay 토글이 round-trip 되지 않던 문제를 수정했다.

### 왜
- URL의 stale query와 chart/timeline 날짜 불일치가 남아 있으면 사용자가 화면 제어가 고장 난 것으로 느끼게 된다.
- preset과 overlay 매핑이 어긋나면 저장/복원 UX가 핵심 작업 화면으로서 신뢰를 잃는다.

### 어떻게
- history range select는 canned range 선택 시 `from`, `to`, `event`를 같이 초기화하고, custom 기간일 때는 `직접 선택` 상태를 표시하도록 조정했다.
- real provider는 filtered series 범위 안으로 들어오는 뉴스만 history timeline에 포함하고, 뉴스 날짜를 가장 가까운 유효 캔들 날짜로 정렬한다.
- radar preset은 우측 패널용 `activeSector`가 아니라 실제 query filter인 `selectedSectorParam`만 저장하도록 변경했다.
- stock rule preset은 `guideIds`/`controlsEventMarkers` 계약과 legacy 매핑을 함께 지원해 guide와 event marker overlay를 안정적으로 복원하게 했다.

### 영향 범위
- `apps/web/features/history/components/history-page.tsx`
- `apps/web/features/radar/components/radar-workbench.tsx`
- `apps/web/features/stocks/components/stock-detail-page.tsx`
- `apps/web/lib/research/types.ts`
- `apps/api/app/schemas/stocks.py`
- `apps/api/app/services/providers/real.py`
- `apps/api/prompts/stock_detail/output.schema.json`

## 2026-03-26 11:10 KST
### 무엇을
- `packages/contracts`를 추가하고 overview/radar/stocks/history runtime JSON schema와 web TypeScript 계약을 한 위치로 모았다.
- API prompt loader가 `packages/contracts/schemas/*.schema.json`을 우선 읽도록 바꿨다.
- 루트 `package.json`, `pnpm-workspace.yaml`, `.gitignore`, `.editorconfig`를 추가해 모노레포 실행 경로를 정리했다.
- 루트 README, `apps/web/README.md`, `apps/api/README.md`를 실제 실행/검증 경로 기준으로 다시 정리했다.
- `docs/prompts/00-08` 문서를 복구해 `docs/codex/prompt-order.md`와 실제 repo 경로를 맞췄다.
- 공통 계약 패키지 채택 결정을 ADR로 추가했다.

### 왜
- 공통 계약 패키지가 빠져 있어 web loader 타입과 API schema가 따로 움직일 위험이 있었다.
- 루트 workspace 파일이 없어 모노레포 실행 경로와 문서가 어긋나 있었다.
- `docs/codex/prompt-order.md`가 가리키는 `docs/prompts/*`가 실제 저장소에 없어 작업 순서 문서가 깨져 있었다.

### 어떻게
- `packages/contracts/schemas`에 페이지별 schema를 두고, `packages/contracts/src/index.ts`에서 web 타입과 raw API 응답 타입을 함께 제공했다.
- `apps/web/lib/research/types.ts`는 계약 패키지를 재수출하는 shim으로 축소했다.
- overview/radar/stocks/history loader의 inline API 타입을 계약 패키지 타입으로 교체했다.
- 실행 문서는 루트 기준 명령과 앱 디렉터리 직접 실행 경로를 둘 다 적었다.

### 영향 범위
- `package.json`
- `pnpm-workspace.yaml`
- `.gitignore`
- `.editorconfig`
- `README.md`
- `apps/web/README.md`
- `apps/api/README.md`
- `apps/api/app/services/prompt_loader.py`
- `apps/web/lib/research/types.ts`
- `apps/web/features/overview/lib/get-overview-snapshot.ts`
- `apps/web/features/radar/lib/get-radar-workspace.ts`
- `apps/web/features/stocks/lib/get-stock-workstation.ts`
- `apps/web/features/history/lib/get-history-replay.ts`
- `packages/contracts/*`
- `docs/prompts/*`
- `docs/adr/ADR-0006-공통-계약-패키지-채택.md`
## 2026-03-26 13:40 KST
### 무엇을
- `docs/architecture/workspace-blueprint.md`를 `packages/contracts` 기준의 canonical schema source로 정리했다.
- `apps/api/AGENTS.md`에 runtime JSON schema의 단일 원천과 prompt compatibility copy 역할을 명시했다.
### 왜
- prompt 본문과 output schema의 역할을 문서에서 혼동하지 않도록 하기 위해서다.
### 어떻게
- runtime JSON schema canonical source와 compatibility copy의 구분을 문서 끝에 보강했다.
### 영향 범위
- 문서/릴리즈 자료만 변경되며 runtime 코드는 바뀌지 않는다.

## 2026-03-26 15:20 KST
### 무엇을
- `scripts/check_contract_parity.py`가 Pydantic 실제 required 필드 기준으로 `packages/contracts`, Pydantic schema, legacy prompt output schema copy의 drift를 검증하도록 보강했다.
- web 4개 loader와 화면 상단 `dataSource` 배지로 live / mock / fixture / fixture fallback 상태를 구분해 silent fallback을 없앴다.
- `packages/contracts` canonical source와 compatibility copy 역할을 README / AGENTS / workspace blueprint에 다시 맞췄다.

### 왜
- canonical contract와 Pydantic actual behavior가 어긋나면 validation이 거짓 양성 또는 거짓 음성을 만들 수 있다.
- mock research data가 live data처럼 보이면 리서치 화면의 신뢰성이 무너진다.

### 어떻게
- parity guard가 `model_fields[field].is_required()` 기준으로 required 집합을 계산하게 바꿨다.
- API transport failure는 release-like mode에서 에러로 올리고, 개발/허용 환경에서만 fixture fallback을 사용하며 화면에서는 항상 데이터 출처 상태를 명시한다.
- `apps/api/prompts/*/output.schema.json`은 compatibility copy임을 문서와 schema comment로 고정했다.

### 영향 범위
- `scripts/check_contract_parity.py`
- `apps/web/lib/server/research-api.ts`
- `apps/web/features/overview/lib/get-overview-snapshot.ts`
- `apps/web/features/radar/lib/get-radar-workspace.ts`
- `apps/web/features/stocks/lib/get-stock-workstation.ts`
- `apps/web/features/history/lib/get-history-replay.ts`
- `apps/web/components/research/data-source-notice.tsx`
- `packages/contracts/*`
- `apps/api/app/services/prompt_loader.py`
- `apps/api/app/services/page_runtime.py`
- `apps/api/AGENTS.md`
- `docs/architecture/workspace-blueprint.md`

## 2026-04-08 01:45 KST
### 무엇을
- Added root scripts for `pnpm smoke:api`, `pnpm verify:web`, `pnpm verify:api`, `pnpm verify:standard`, and `pnpm verify:standard:json`.
- Added `scripts/api_smoke.py` and `scripts/verify_workspace.py` as reusable validation entrypoints.
- Updated AGENTS, README, app READMEs, Codex operating docs, and prompts so unattended work closes with one standard verification loop.
- Recorded the verification-gate decision in `docs/adr/ADR-0007-autonomous-verification-gate.md`.

### 왜
- The repo already had the checks, but they were scattered and easy for an autonomous agent to skip or partially run.
- The API smoke test was hard to reuse because it only existed as an inline command.
- Unattended work needed an explicit end-to-end close-out contract.

### 어떻게
- Replaced the root verification path with a single standard gate and added smaller web/api slices for failure isolation.
- Moved the FastAPI smoke test into `scripts/api_smoke.py` and grouped all checks in `scripts/verify_workspace.py`.
- Added unattended-mode guidance in AGENTS, README, Codex docs, and a new prompt file.

### 영향 범위
- `package.json`
- `scripts/api_smoke.py`
- `scripts/verify_workspace.py`
- `README.md`
- `AGENTS.md`
- `apps/web/README.md`
- `apps/web/AGENTS.md`
- `apps/api/README.md`
- `apps/api/AGENTS.md`
- `docs/codex/prompt-order.md`
- `docs/prompts/08-tests-docs-changelog.md`
- `docs/prompts/09-autonomous-delivery.md`
- `docs/adr/ADR-0007-autonomous-verification-gate.md`
## 2026-04-08 03:40 KST
### ???
- ?? 4?? IA? ??? ? `/news`, `/calendar` ?? route? ?? API/??? ????.
- Alpha Vantage `EARNINGS_CALENDAR` / `IPO_CALENDAR` CSV ??? ????? client? ????.
- OpenDART ?? ?? ??/?? ??? `news`, `calendar`? ????.
- provider env ??, env example, README, manifest, ADR, ??/???/?? ??? ?? ????.

### ?
- ???? ?? ???? ??? ??? ???? ??? ??? ? ??? ??.
- ??? ??? ?? sidebar 4??? ???? ?? ??? ?? route ??? ????.
- real `/calendar` ??? CSV helper ?? ??? ???, unattended ??? ?? ?? ??? ??? ? ?? ??? ???? ??.

### ???
- backend? `extended_real` / `extended_mock` provider? `news`, `calendar` router / schema / contract / prompt? ????.
- web? `/news`, `/calendar` route? loader, fixture, topbar route context, overview CTA? ????.
- `scripts/api_smoke.py`? schema validation?? ????? ???? `pnpm verify:standard`? ?? ??? ?? ?????.
- page manifest, component manifest, design memory, ADR-0008, env/deployment/test docs, OMX plan/log, issue/PR draft? ?? ???.

### ?? ??
- `apps/api/app/services/clients/alpha_vantage.py`
- `apps/api/app/services/clients/open_dart.py`
- `apps/api/app/services/providers/extended_real.py`
- `apps/api/app/services/providers/extended_mock.py`
- `apps/api/app/routers/news.py`
- `apps/api/app/routers/calendar.py`
- `apps/web/app/news/page.tsx`
- `apps/web/app/calendar/page.tsx`
- `apps/web/features/news/*`
- `apps/web/features/calendar/*`
- `apps/web/lib/navigation.ts`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/adr/ADR-0008-auxiliary-research-routes.md`

## 2026-04-09 01:20 KST
### 무엇을
- `pnpm verify:release`, `pnpm verify:release:json`, `scripts/verify_release_readiness.py`를 추가해 real-provider 전용 릴리스 게이트를 만들었다.
- API에 `/readyz?probe=config|remote` readiness 엔드포인트를 추가하고 `/health`와 역할을 분리했다.
- web loader가 production 후보에서 API URL 미설정을 fixture로 숨기지 않도록 hardening했다.
- `apps/web/.env.example`, `apps/api/Dockerfile`, root `.dockerignore`를 추가했다.
- `/`, `/overview`, `/radar`를 dynamic route로 고정하고 `apps/web/next.config.ts`에 `experimental.cpus=1`을 적용해 Codex/Windows 환경의 build worker pressure를 낮췄다.
- README, app README, deployment/api/env/test docs, ADR-0009를 갱신했다.

### 왜
- 기존 `pnpm verify:standard`는 개발 회귀 검증에는 충분했지만, 실 provider 3종 정상 여부를 배포 승인 기준으로 증명하지 못했다.
- web fixture fallback이 production 후보에서도 조용히 동작하면 실제 배포 리스크를 숨길 수 있었다.
- 실제 배포 실행은 범위 밖이지만, deploy-ready 상태를 코드/문서/명령으로 고정할 필요가 있었다.

### 어떻게
- FastAPI readiness 서비스를 새로 만들고 Alpha Vantage / OpenDART / OpenAI probe를 분리했다.
- release 검증 스크립트가 env 존재, fallback 금지, readiness remote probe, 6개 route smoke를 한 번에 점검하도록 구성했다.
- web 각 route loader에 `assertResearchApiConfigured()`를 추가해 production 후보에서 API URL 미설정을 즉시 에러로 승격했다.
- build 시점의 worker spawn 민감도를 낮추기 위해 live research 성격의 정적 route를 dynamic으로 전환하고 Next experimental cpu 수를 1로 제한했다.
- deploy template와 env example을 최소 변경으로 추가하고 관련 문서를 동기화했다.

### 영향 범위
- `package.json`
- `scripts/api_smoke.py`
- `scripts/verify_workspace.py`
- `scripts/verify_release_readiness.py`
- `apps/api/app/main.py`
- `apps/api/app/services/readiness.py`
- `apps/api/app/services/clients/openai_responses.py`
- `apps/api/Dockerfile`
- `apps/api/README.md`
- `apps/web/lib/server/research-api.ts`
- `apps/web/app/page.tsx`
- `apps/web/app/overview/page.tsx`
- `apps/web/app/radar/page.tsx`
- `apps/web/next.config.ts`
- `apps/web/features/overview/lib/get-overview-snapshot.ts`
- `apps/web/features/radar/lib/get-radar-workspace.ts`
- `apps/web/features/stocks/lib/get-stock-workstation.ts`
- `apps/web/features/history/lib/get-history-replay.ts`
- `apps/web/features/news/lib/get-news-feed.ts`
- `apps/web/features/calendar/lib/get-calendar-board.ts`
- `apps/web/.env.example`
- `apps/web/README.md`
- `.dockerignore`
- `README.md`
- `docs/deployment.md`
- `docs/api-integration.md`
- `docs/env-checklist.md`
- `docs/test-strategy.md`
- `docs/adr/ADR-0009-deploy-ready-release-gate.md`
## 2026-04-11 10:20 KST
### ???
- ?? 4?? ?? ??? Gemini ?? provider? deterministic fallback? ????.
- `RESEARCH_LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_BASE_URL` env? ????.
- readiness? OpenAI ?? ??? ??? OpenAI/Gemini/none ??? ????? ????.

### ?
- `OPENAI_API_KEY`? ?? ? ?? 4?? real path? ?? ??? ??? ??? ??.
- ?? ?? ??? ?? LLM ??? ??? ???/?? ?? ??? ????.

### ???
- `ResearchSummaryClient`? OpenAI -> Gemini -> deterministic fallback ??? ?? provider? ???? ??.
- Gemini REST structured output client? ????, ?? ? source-based deterministic summary? ???? ????.
- env example? README/docs? ?? ????.

### ?? ??
- `apps/api/app/config.py`
- `apps/api/app/services/clients/gemini_responses.py`
- `apps/api/app/services/clients/summary_router.py`
- `apps/api/app/services/deterministic_summary.py`
- `apps/api/app/services/providers/real.py`
- `apps/api/app/services/readiness.py`
- `apps/api/.env.example`
