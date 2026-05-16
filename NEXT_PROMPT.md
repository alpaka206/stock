1. 실제 provider key와 Perso 계정을 넣은 환경에서 `stock_BE` ingest, submit, sync smoke test를 수행한다.
2. SMTP를 연결하고 리포트 미리보기, 저장, 실제 이메일 발송까지 운영 smoke test를 수행한다.
3. `stock` develop에서 `/workspace`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`를 운영 API 기준으로 다시 확인한다.
4. Google OAuth 운영 client, 결제, 구독별 기능 제한을 접근 제어 없이 화면과 API 계약부터 확장한다.
5. develop 누적 변경이 안정화되면 `develop -> main` release PR만 생성하고 병합은 사용자가 직접 진행한다.
