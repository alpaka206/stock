# 목표
`apps/web`를 금융 리서치 워크스페이스용 프론트엔드로 스캐폴딩한다.

# 참고 문서
- apps/web/AGENTS.md
- docs/design/design-memory.md
- docs/architecture/component-manifest.yaml

# 할 일
- 공통 layout, sidebar/topbar, theme provider, query provider를 구성한다.
- AG Grid 공통 래퍼와 locale 설정(한국어 우선)을 준비한다.
- 공통 UI 토큰(간격, 카드, 숫자 스타일)을 정리한다.
- 페이지별 폴더를 만든다.
- feature 폴더를 만든다.
  - `features/grid`
  - `features/chart`
  - `features/filters`
  - `features/watchlist`
  - `features/sector`
  - `features/history`
- 샘플 mock 데이터와 개발용 fixture 구조를 추가한다.

# 제약
- 비즈니스 로직을 `page.tsx`에 몰아넣지 않는다.
- 사용자 상태와 서버 상태를 분리한다.
- 그리드는 AG Grid 기준으로 공통화한다.

# 완료 조건
- 공통 shell이 적용된다.
- 다크모드가 동작한다.
- AG Grid 샘플 화면이 동작한다.
- 문서와 changelog가 갱신된다.
