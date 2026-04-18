# Stock Reference Blueprint

## 목표
`stock`를 단순 시세 조회 사이트가 아니라, 국장과 미장을 한 번에 연구할 수 있는 주식 분석 워크스페이스로 만든다.

핵심은 두 층을 동시에 만족시키는 것이다.

- 초보자: "지금 이 종목이 왜 위험한지, 왜 지켜볼 만한지"를 쉽게 이해한다.
- 숙련 사용자: 차트, 거래량, 공시, 뉴스, 캘린더, 섹터 문맥을 한 화면에서 빠르게 읽는다.

## 참고 서비스

### 1. TradingView
참고 링크: [TradingView Stock Screener](https://www.tradingview.com/support/solutions/43000718866-tradingview-stock-screener-trade-smarter-not-harder/)

가져올 점:
- 차트와 스크리너가 한 흐름 안에서 이어지는 구조
- 기술 지표와 필터를 동시에 보는 탐색 경험
- 저장 가능한 스크린과 watchlist 흐름

피해야 할 점:
- 기능은 강하지만 초보자에게는 진입 장벽이 높다
- 설명보다 도구 중심이라 해석형 안내가 약하다

### 2. Koyfin
참고 링크: [Koyfin Market Dashboards](https://www.koyfin.com/features/market-dashboards/)

가져올 점:
- 시장 전반을 한 화면에 압축하는 대시보드 밀도
- 글로벌 매크로, 섹터, 팩터, 수익률 곡선을 한 문맥으로 엮는 방식
- 비교 중심의 연구형 패널 구성

피해야 할 점:
- 정보 밀도가 높아 초보자에게는 부담이 될 수 있다

### 3. Finviz
참고 링크: [Finviz Screener Help](https://finviz.com/help/screener.ashx)

가져올 점:
- 빠른 스캔과 스크리너 중심 사고방식
- 히트맵, 섹터 흐름, 시각적 우선순위 정리
- 핵심 숫자를 짧고 강하게 배치하는 방식

피해야 할 점:
- 화면이 기능 위주라 친절한 해설형 UX는 약하다

### 4. Nasdaq
참고 링크: [Nasdaq Stock Screener](https://www.nasdaq.com/market-activity/stocks/screener), [Nasdaq Market Activity](https://www.nasdaq.com/market-activity/)

가져올 점:
- 종목 요약, 차트, 시세, 장전/장후 흐름, 데이터 지연 안내
- 데이터 출처와 지연 상태를 명확히 드러내는 방식

피해야 할 점:
- 초보자 친화 설명은 상대적으로 약하다

### 5. Investing.com
참고 링크: [Stocks Technical Indicators](https://www.investing.com/technical/stocks-indicators)

가져올 점:
- 이동평균, RSI, MACD, Stochastic 등을 표로 빠르게 읽는 방식
- 여러 기술 지표를 한 번에 요약하는 패턴

피해야 할 점:
- "Strong Buy / Strong Sell" 같은 표현을 그대로 복제하면 예측 서비스처럼 보일 수 있다

## 공식 데이터 출처 우선순위

### 한국
- [KRX 정보데이터시스템](https://data.krx.co.kr/)
  - 시세, 거래실적, 시장 통계, 상장종목 검색
- [KIND](https://kind.krx.co.kr/common/JLDDST35000.html)
  - 거래소 공시, 상장 관련 정보, IR/공시 채널
- [DART](https://dart2.fss.or.kr/)
  - 정기보고서, 주요사항보고서, 최근공시
- [OpenDART](https://opendart.fss.or.kr/)
  - API 기반 공시 활용

### 미국
- [SEC EDGAR](https://www.sec.gov/search-filings)
  - 10-K, 10-Q, 8-K, insider filings, full-text filing search
- [Nasdaq Market Activity](https://www.nasdaq.com/market-activity/)
  - 종목 시세, 장전/장후 데이터 문맥, 스크리너

## 제품 원칙

### 1. 초보자와 숙련자를 동시에 만족시킨다
- 초보자용: 한 줄 요약, 쉬운 설명, 왜 그런 해석이 나왔는지 근거를 문장으로 제공
- 숙련자용: 이동평균 배열, 거래량 변화, 공시 이벤트, 뉴스 타임라인, 섹터 비교를 동시에 제공

### 2. 차트는 예쁜 장식이 아니라 핵심 판단 보조 도구다
- 기본 오버레이: 5일선, 10일선, 20일선, 60일선, 120일선
- 기본 보조 영역: 거래량
- 패턴 도감: cup with handle, double bottom, saucer base, flat base, ascending base 등 대표 패턴 카드
- 기본 해석 항목:
  - 정배열/역배열
  - 단기선-중기선 교차
  - 거래량 급증/급감
  - 전고점/전저점 돌파 여부
  - 갭 발생 여부
  - 장대 양봉/음봉 의미
  - 이벤트 이후 추세 유지 여부
  - 현재 차트가 어떤 패턴에 유사한지, 어느 단계인지, 무효화 조건이 무엇인지

### 3. 차트 해석은 설명형이어야 한다
좋은 표현 예시:
- "단기선이 20일선 위에서 유지되고 거래량이 동반되어 상승 추세 유지 가능성을 지켜볼 구간입니다."
- "5일선과 10일선이 꺾였고 최근 상승 구간보다 거래량이 줄어 단기 탄력이 약해질 수 있어 주의가 필요합니다."
- "60일선 아래로 재진입하면 중기 추세 약화로 볼 수 있어 지지 여부를 먼저 확인해야 합니다."
- "현재 구조는 flat base에 가깝지만 박스 상단 돌파 확인 전이라 패턴 진행 중으로 보는 편이 안전합니다."
- "double bottom 유사 흐름이지만 넥라인 돌파 전이라 확인 구간으로 보는 편이 좋습니다."

피해야 할 표현:
- "무조건 오른다"
- "곧 폭등한다"
- "반드시 떨어진다"

### 4. 출처와 지연 상태를 숨기지 않는다
- 각 데이터 블록에 출처 표시
- 실시간인지, 지연 시세인지, 전일 기준인지 표시
- unavailable일 때는 빈칸이 아니라 이유를 표시

## 필수 화면 방향

### overview
- 오늘의 한국/미국 시장 방향을 10초 안에 이해
- 주요 지수, 섹터 강도, 리스크 요인, 캘린더를 먼저 보여줌

### radar
- 국장/미장 필터 전환
- 상승/하락/거래대금/거래량/갭/52주 고가 근처 등 프리셋 제공
- 히트맵과 그리드가 함께 움직여야 함

### stocks/[symbol]
- 차트가 메인
- 차트 옆에 해석 패널, 패턴 도감, 현재 유사 패턴 카드, 뉴스, 공시, 실적 일정, 유사 종목 비교
- 초보자용 요약과 숙련자용 지표 패널을 함께 제공

### history
- 가격 흐름과 이벤트 타임라인을 동기화
- 특정 급등/급락 구간에 왜 그런 이벤트가 있었는지 문맥 제공

## 경고 및 안전 원칙
- 이 서비스는 투자 자문이 아니라 정보 해석 보조 도구다
- 지표 해석은 설명형으로 유지하고, 단정적 매수/매도 권유 문구는 피한다
- 데이터가 없거나 지연되면 그 사실을 먼저 보여준다

## 구현 체크리스트
- 국장/미장 검색 흐름 통합
- 이동평균선 5/10/20/60/120 기본 제공
- 차트 해석 패널 한국어 설명
- 패턴 도감 카드 UI
- 현재 차트 유사 패턴 카드
- 공시, 뉴스, 이벤트 타임라인 연동
- 출처/지연 상태 표기
- 초보자 모드와 숙련자 모드 공존
