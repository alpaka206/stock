# 저장소 공통 지침

이 저장소는 **AI 기반 주식 리서치 워크스페이스**를 만드는 프로젝트다.
메인 내비게이션은 아래 4개 화면으로 고정한다.

1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

이 프로젝트의 핵심 목표는 **뉴스, 차트, 섹터, 수급, 옵션/공매도, 점수, 과거 이벤트를 한 흐름 안에서 보게 하는 것**이다.
단순한 뉴스 앱이나 주문 앱처럼 만들지 않는다.

## 가장 먼저 읽을 문서
Codex는 구조/디자인/기능을 추측하지 말고 아래 문서를 먼저 읽고 작업한다.

- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/codex/prompt-order.md`

## 제품 원칙
- 사용자 노출 문구는 기본적으로 한국어를 사용한다.
- 수익 보장, 확정 수익, 무조건 상승 같은 표현을 금지한다.
- 직접적인 매수/매도 지시 문구를 기본 UI 문구로 쓰지 않는다.
- 우선검토 / 관심 / 조건부 강세 / 무효화 / 리스크 확대 같은 표현을 우선 사용한다.
- 가격, 뉴스, 리포트, 기술적 레벨, 점수는 출처나 계산 근거 없이 만들어내지 않는다.
- 수치 데이터는 가능한 한 결정론적 로직으로 계산하고, LLM은 요약/설명/랭킹 사유/문장화에 집중시킨다.


## 비용/라이선스 원칙
- 현재 단계에서는 유료 라이선스 전제를 두지 않는다.
- AG Grid는 Community 에디션 범위 안에서만 설계한다.
- Enterprise 전용 기능(row grouping, pivot, columns tool panel, 고급 엑셀 UX)에 의존하지 않는다.
- 무료 범위에서 동일한 UX가 필요하면 좌측 트리/뷰 모드/사전 그룹화 데이터/커스텀 툴바로 대체한다.
- 새로운 라이브러리를 추가할 때는 무료 사용 가능 여부와 라이선스를 README 및 ADR에 기록한다.

## 문서화 규칙
- 기존 문서를 삭제하거나 과거 결정을 덮어쓰지 않는다.
- 구조/기능/디자인/정책이 바뀌면 아래를 함께 갱신한다.
  - `docs/changes/CHANGELOG_APPEND_ONLY.md`
  - 관련 ADR 문서 (`docs/adr/`)
  - 변경된 페이지의 manifest
- 변경 로그는 append-only 원칙을 따른다.
- "무엇을", "왜", "어떻게", "영향 범위"를 기록한다.

## 완료 조건
작업이 끝났다고 말하기 전에 아래를 확인한다.
- 관련 문서와 코드가 함께 갱신되었는가
- 타입체크/린트/테스트 실행 경로가 README와 일치하는가
- 새 기능이 4개 메인 화면 구조를 깨지 않는가
- 화면별 역할이 page-manifest와 일치하는가

## 폴더 역할
- `apps/web`: Next.js 프론트엔드
- `apps/api`: FastAPI 백엔드
- `apps/api/prompts`: 런타임 AI 프롬프트와 출력 스키마
- `docs/architecture`: IA, 페이지/컴포넌트 manifest
- `docs/design`: 디자인 메모리와 UI 원칙
- `docs/adr`: 아키텍처 결정 기록
- `docs/changes`: append-only 변경 기록
- `docs/prompts`: Codex에게 순서대로 보낼 작업 프롬프트
- `scripts`: 초기 설정/유틸 스크립트 예시
