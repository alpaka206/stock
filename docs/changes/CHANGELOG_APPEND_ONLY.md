# CHANGELOG (Append Only)

## 2026-03-15 13:00 KST
### 추가
- 4개 메인 페이지 중심 IA 정의
- 루트/웹/API 3개의 AGENTS.md 초안 추가
- Codex 프롬프트 순서 문서 추가
- 페이지/컴포넌트 manifest 추가
- 디자인 메모리 문서 추가
- 프로젝트 디렉터리 구조 초안 추가

### 이유
- 사용자가 4개 화면 구조를 반복 설명하지 않아도 Codex가 지속적으로 참조할 수 있게 하기 위해
- 이후 구조 변경 때 무엇이 바뀌었고 왜 바뀌었는지 추적할 수 있게 하기 위해

### 영향
- 이후 구현 작업은 AGENTS.md, manifest, design-memory를 먼저 읽는 방식으로 진행한다.

## 2026-03-15 - 무료 그리드 전략으로 조정
- 무엇을: AG Grid 전제를 AG Grid Community 기준으로 명확화하고 Enterprise 의존 문구를 제거했다.
- 왜: 초기 단계에서는 유료 라이선스 비용을 전제하지 않기로 결정했기 때문이다.
- 어떻게: README, 루트/웹 AGENTS, manifest를 갱신하고 ADR-0003을 추가했다.
- 영향 범위: `/radar` grid 구현 방식, 컬럼 토글 UX, 그룹 뷰 구조, Codex 프롬프트 기본 방향

## 2026-03-16 09:40 KST
- 무엇을: `apps/web` 에 공통 shell, theme/query provider, AG Grid 공통 래퍼, feature 폴더, 개발용 fixture, 메인 4개 화면 스캐폴드를 추가했다.
- 왜: 금융 리서치 워크스페이스의 공통 UX 골격과 mock 데이터 흐름을 먼저 고정해야 이후 API 연동과 페이지 구현이 흔들리지 않기 때문이다.
- 어떻게: App Router route 를 thin wrapper 로 유지하고 `features/*`, `components/shell`, `components/providers`, `dev/fixtures`, `lib/tokens` 구조로 분리했다. AG Grid Community 한국어 locale 설정과 다크모드 토글을 함께 구성했고, README/component-manifest/design-memory/ADR 을 갱신했다.
- 영향 범위: `apps/web` 전체 레이아웃, 메인 4개 화면 기본 UX, AG Grid 사용 방식, 향후 서버 상태 연결 지점

## 2026-03-17 00:35 KST
- 무엇을: `apps/api` 에 FastAPI 진입점, 화면 단위 router, Pydantic 응답 모델, prompt loader, JSON schema validator, mock/real provider 분리 구조를 추가했다.
- 왜: 메인 4개 화면을 API 단에서 독립적으로 확장하고, 런타임 프롬프트 로딩과 응답 검증 흐름을 미리 고정해야 이후 실제 데이터/LLM 연동 시 구조가 흔들리지 않기 때문이다.
- 어떻게: `/overview`, `/radar`, `/stocks/{symbol}`, `/history` router 를 등록하고 `app/services/prompt_loader.py`, `app/services/schema_validator.py`, `app/services/providers/*` 를 구성했다. mock provider 는 즉시 응답 가능하게 만들고 real provider interface 는 자리만 분리했다.
- 영향 범위: `apps/api` 전체 부트스트랩, 프롬프트 파일 로딩 방식, 응답 schema 관리 방식, 웹앱의 향후 서버 연동 계약

## 2026-03-17 02:10 KST
- 무엇을: `apps/api` real provider 에 Alpha Vantage 실데이터와 OpenAI structured output 호출을 연결하고, page별 output schema 와 sourceRefs 계약을 강화했다.
- 왜: 프론트 페이지를 실제 API 기준으로 붙이기 전에 데이터 수집, 요약, 출처 추적, 누락 데이터 처리 방식이 먼저 고정돼야 하기 때문이다.
- 어떻게: `app/services/clients/*` 에 Alpha Vantage/OpenAI client 를 추가하고 `app/services/providers/real.py` 에 화면별 fact builder 를 구현했다. `sourceRefs`, `missingData`, `confidence` 를 typed object 로 승격했고 prompts/output schema/README/.env.example/ADR-0005 를 갱신했다.
- 영향 범위: `apps/api` 실데이터 연동 방식, OpenAI 응답 구조, 프론트엔드 서버 상태 계약, 향후 추가 provider 설계
