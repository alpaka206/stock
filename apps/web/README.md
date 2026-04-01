# apps/web

금융 리서치 워크스페이스의 Next.js 프론트엔드다.

고정 route:

- `/overview`
- `/radar`
- `/stocks/[symbol]`
- `/history`

## 실행

루트 기준:

```powershell
pnpm install
pnpm dev:web
```

앱 디렉터리 직접 실행:

```powershell
cd apps/web
pnpm dev
```

## 검증

루트 기준:

```powershell
pnpm lint:web
pnpm typecheck:web
pnpm build:web
```

앱 디렉터리 기준:

```powershell
cd apps/web
pnpm lint
pnpm typecheck
pnpm build
```

## 구조 원칙

- route 파일은 thin wrapper를 유지한다
- 화면 조립과 상태 로직은 `features/*` 아래에 둔다
- 사용자 상태와 서버 상태를 분리한다
- grid는 AG Grid Community 범위 안에서만 사용한다
- 사용자 노출 문구는 한국어 우선이다
- API 우선 + fixture fallback 구조를 유지하되, live / mock / fixture 상태를 화면 상단 배지로 명시한다

## 공통 계약

- UI/loader 타입 기준 패키지: `packages/contracts`
- web re-export shim: `lib/research/types.ts`
- API fetch adapter는 `packages/contracts`의 raw response 타입을 기준으로 mapping 한다
