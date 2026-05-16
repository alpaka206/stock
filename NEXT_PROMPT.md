1. `stock_BE` develop에서 provider key와 Perso 계정을 연결해 ingest, submit, sync smoke test를 수행한다.
2. `stock` develop에서 `/workspace`, `/overview`, `/radar`, `/stocks/NVDA`, `/history`를 운영 API 기준으로 다시 확인한다.
3. Google OAuth, 결제, 구독별 기능 제한을 접근 제어 없이 화면과 API 계약부터 확장한다.
4. 리포트 이메일 템플릿과 주간/일간 스케줄러를 실제 발송 플로우로 연결한다.
5. develop 누적 변경이 안정화되면 `develop -> main` release PR만 생성하고 병합은 사용자가 직접 진행한다.
