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
