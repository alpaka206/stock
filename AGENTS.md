# AGENTS.md

## 프로젝트 목적

이 저장소는 미국 주식과 한국 주식을 함께 다루는 주식 리서치 워크스페이스다. 사용자는 한곳에서 시장 흐름, 종목별 가격과 차트, 뉴스, 공시, 이벤트, 과거 판단 기록을 빠르게 확인할 수 있어야 한다.

## 우선 완성할 화면

1. `/overview`
2. `/radar`
3. `/stocks/[symbol]`
4. `/history`

보조 화면은 `/news`, `/calendar`를 유지하되 핵심 흐름을 방해하지 않아야 한다.

## 먼저 읽을 문서

- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/codex/prompt-order.md`
- `docs/api-integration.md`
- `docs/env-checklist.md`

## 현재 운영 원칙

- 무한 루프형 자동화와 외부 채팅 브리지 자동화는 사용하지 않는다.
- 브랜치 기준은 `develop`이며, 작업은 issue-linked branch에서 진행한다.
- `main`, `develop`에 직접 커밋하거나 직접 push하지 않는다.
- 이슈, 커밋, PR 제목은 `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `ci:`, `test:`, `perf:` 중 하나로 시작한다.
- 커밋 메시지와 PR 설명은 한국어 중심으로 작성한다.
- `[codex]` 같은 접두사는 쓰지 않는다.

## 데이터 원칙

- 출처 없는 가격, 뉴스, 점수, 레벨은 만들지 않는다.
- 실제 API가 없거나 실패해 fixture/fallback을 보여줄 때는 화면과 데이터 설명에 반드시 `(목데이터)`를 표시한다.
- 사용자가 작성한 판단 기록과 서버에서 관리해야 하는 값은 서버 API를 통해 저장한다.
- 운영에서는 `DATABASE_URL` 기반 저장소를 우선 사용한다. 로컬 fallback 파일 저장소는 개발 편의용이다.
- API 응답 계약은 `packages/contracts`를 기준으로 맞춘다.

## 백엔드 원칙

- API는 FastAPI를 기본으로 유지하되, 규모가 커지면 별도 백엔드 저장소로 분리할 수 있다.
- 프런트는 API 계약과 환경변수만 보고 동작해야 하며 내부 DB 구현에 의존하지 않는다.
- 저장 동작은 가능하면 DB 트랜잭션으로 처리한다.
- 파일 fallback은 임시 파일 작성 후 rename으로 교체해 중간 손상 가능성을 줄인다.
- 관계형 데이터가 필요한 기능은 정규화, 외래키, cascade 정책, 원자성을 먼저 설계한다.

## 프런트엔드 원칙

- 실제 사용자가 바로 이해할 수 있는 문구를 쓴다. 개발자용 설명을 화면에 노출하지 않는다.
- 과한 장식, AI스러운 그라데이션, 의미 없는 카드 중첩을 피한다.
- 레이아웃은 빠르게 스캔할 수 있게 밀도 있게 구성한다.
- 표, 차트, 필터는 고정된 크기와 반응형 제약을 둬 reflow를 줄인다.
- 텍스트 letter spacing은 0을 기준으로 한다.
- i18n 기본 언어는 한국어, 영어, 일본어, 중국어다.

## 검증

기본 검증은 아래를 우선한다.

```bash
pnpm verify:standard
pnpm verify:release
```

프런트 변경이 있으면 최소한 아래 경로를 브라우저에서 확인한다.

- `/overview`
- `/radar`
- `/stocks/NVDA`
- `/history?symbol=NVDA`

## 보안

- `.env`, `.env.*`, API 키, 토큰, 웹훅 URL은 커밋하지 않는다.
- `apps/web/.env`, `apps/api/.env`, 개인 로컬 설정 파일은 값 확인 없이 존재 여부만 다룬다.
- 커밋 전 `pnpm guard:no-secrets` 또는 `pnpm verify:standard`를 실행한다.
