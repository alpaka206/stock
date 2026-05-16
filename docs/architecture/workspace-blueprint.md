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

### API

- FastAPI
- Pydantic
- SQLAlchemy
- Postgres 우선, 개발용 파일 저장 fallback
- Alpha Vantage, OpenDART, 선택 LLM provider

### 계약

- `packages/contracts`가 프런트와 백엔드 타입의 기준이다.
- API schema, prompt output schema, web type이 어긋나면 `scripts/check_contract_parity.py`가 실패해야 한다.

## 데이터 저장

- 사용자 판단 기록은 `/snapshots` API로 저장한다.
- `DATABASE_URL`이 있으면 Postgres 트랜잭션을 사용한다.
- `DATABASE_URL`이 없으면 `data/runtime/research_snapshots.json` 파일 저장소를 사용한다.
- 파일 저장소는 임시 파일 작성 후 rename으로 교체해 중간 손상을 줄인다.

## 배포

- 로컬과 스테이징은 Docker Compose의 `web`, `api`, `db` 조합을 기본으로 한다.
- Web은 Vercel 배포도 가능하다.
- API는 Docker 기반 배포를 권장한다.
- 운영 후보에서는 `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`를 설정한다.
