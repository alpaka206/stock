1. `stock_BE`의 Spring Boot 저장 API를 기준으로 프런트 API adapter 전환 계획을 코드 단위로 나눈다.
2. `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 응답 계약을 Spring Boot 저장 뷰 API로 맞춘다.
3. Alpha Vantage, OpenDART, SEC EDGAR, KRX/KIS 수집 결과를 백엔드 DB에 저장하는 ingest 작업을 추가한다.
4. 사용자 판단 기록, 저장된 보기, 최근 종목을 localStorage에서 서버 저장으로 옮긴다.
5. 로그인/구독/리포트/Perso 더빙 작업은 접근 제한 없이 저장 모델과 API부터 붙인다.
