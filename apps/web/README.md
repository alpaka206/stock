# apps/web

금융 리서치 워크스페이스용 Next.js 프론트엔드다. 메인 화면은 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 4개로 고정한다.

## 실행

```bash
pnpm dev
```

## 검증

```bash
pnpm lint
pnpm typecheck
```

현재 `apps/web` 에 별도 자동 테스트는 아직 없다.

## 스캐폴드 구성

- 공통 shell: 좌측 sidebar + 상단 topbar + 다크모드 토글
- provider: `next-themes`, `@tanstack/react-query`
- grid: AG Grid Community 공통 래퍼 + 한국어 locale
- chart: 개발용 mock 데이터 기반 공통 라인 차트
- fixture: `dev/fixtures/*`
- route: `app/*/page.tsx` 는 thin wrapper, 실제 화면은 `features/*` 에서 조합

## 주요 디렉터리

- `app/`: App Router route entry
- `components/providers/`: theme/query provider
- `components/shell/`: 공통 layout chrome
- `components/research/`: 공통 패널/숫자 표현 컴포넌트
- `features/overview`: overview 화면 조합
- `features/radar`: radar 화면 조합
- `features/stocks`: stock detail 화면 조합
- `features/history`: history 화면 조합
- `features/grid`: AG Grid 공통 설정
- `features/chart`: 공통 차트
- `features/filters`: 공통 필터 칩
- `features/watchlist`: 워치리스트 트리
- `features/sector`: 섹터 요약 패널
- `dev/fixtures`: 개발용 mock fixture

## 원칙

- 비즈니스 로직을 `page.tsx` 에 몰아넣지 않는다.
- 사용자 상태와 서버 상태를 분리한다.
- grid 는 AG Grid Community 기준으로 공통화한다.
- 사용자 노출 문구는 한국어를 우선한다.
