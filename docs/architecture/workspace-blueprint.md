# Stock Desk 워크스페이스 청사진

## 목표

Stock Desk는 미국장과 국내장을 함께 보는 리서치 워크스페이스다. 사용자는 시장 흐름을 먼저 보고, 관심 종목을 좁힌 뒤, 종목 상세와 과거 이벤트를 확인하고, 자신의 판단을 서버에 저장한다.

## 핵심 화면

- `/overview`: 지수, 섹터, 뉴스, 위험 요인을 한눈에 본다.
- `/radar`: 관심 종목을 검색, 필터, 정렬한다.
- `/stocks/[symbol]`: 가격 차트, 기술적 신호, 뉴스, 공시, 판단 기록을 본다.
- `/history`: 과거 이벤트와 가격 반응을 복기한다.

## 기술 스택

### Web

- Next.js App Router
- React Server Components 우선
- TypeScript
- Tailwind CSS
- shadcn/ui
- lucide-react
- next-themes

### Backend

- 별도 저장소 `../stock_BE`
- Spring Boot 3
- Java 17
- Spring Security
- Springdoc OpenAPI
- JPA, Flyway, Postgres
- Redis

### 계약

- `packages/contracts`가 프런트와 백엔드 타입의 기준이다.
- Spring 백엔드는 저장 뷰 API 응답을 이 계약에 맞춘다.
- 프런트는 백엔드 내부 DB 구조가 아니라 API 계약과 환경변수만 의존한다.

## 데이터 저장

- 사용자 판단 기록은 백엔드 `/snapshots` API로 저장한다.
- 시장 데이터, 뉴스, 공시, 캘린더, 리포트 예약, 미디어 작업 상태는 백엔드 DB에서 관리한다.
- 저장 동작은 백엔드 트랜잭션과 외래키/cascade 정책을 따른다.

## 배포

- Web은 Vercel 또는 Docker 기반 Node 호스트를 권장한다.
- Backend는 Spring Boot Docker 서비스를 권장한다.
- 운영 후보에서는 `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`를 설정한다.
