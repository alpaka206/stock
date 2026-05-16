# Web 전용 지침

## 기술 스택

- Next.js App Router
- React Server Components 우선
- TypeScript
- Tailwind CSS
- shadcn/ui
- lucide-react
- next-themes

## 화면 설계 원칙

- 페이지 데이터 로드는 가능한 한 Server Component에서 처리한다.
- 검색, 필터, 탭, 차트 선택, 저장 버튼처럼 상호작용이 필요한 부분만 Client Component로 둔다.
- URL로 공유 가능한 상태는 search params에 둔다.
- 사용자의 판단 기록처럼 서비스 상태에 가까운 값은 서버 API로 저장한다.
- 로컬 스토리지는 언어, 테마, 최근 본 종목, 개인 프리셋처럼 기기별 선호에만 쓴다.
- 표와 차트는 가볍게 렌더링한다. 대규모 그리드 라이브러리는 기본 경로에 싣지 않는다.
- 텍스트는 실제 사용자에게 보이는 말로 쓴다. 개발자용 설명을 화면에 노출하지 않는다.

## 페이지별 기준

### `/overview`

- 상단: 오늘 시장 요약과 데이터 상태
- 중단: 지수, 섹터 흐름, 핵심 뉴스
- 하단: 위험 요인과 누락 데이터

### `/radar`

- 좌측: 폴더, 섹터, 태그, 저장된 보기
- 중앙: 관심 종목 테이블과 정렬/검색
- 우측: 선택 종목 요약, 감지 알림, 섹터 근거, 일정, 리포트

### `/stocks/[symbol]`

- 가격 차트가 중심이다.
- 이동평균, 지지선, 거래량, 상대강도, 이벤트 마커를 사용자가 켜고 끌 수 있어야 한다.
- 판단 기록은 서버 API에 저장한다.

### `/history`

- 종목과 기간을 바꾸면 과거 이벤트 복기 흐름이 유지되어야 한다.
- 이벤트 선택 시 차트 위치와 설명 카드가 함께 바뀐다.
- 저장된 판단 기록을 시간순으로 다시 볼 수 있어야 한다.

## 함께 갱신할 문서

- `docs/architecture/component-manifest.yaml`
- `docs/architecture/page-manifest.yaml`
- `docs/design/design-memory.md`
