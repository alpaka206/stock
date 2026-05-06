현재 라운드 목표
- #160 provider 리팩터링 후속으로 stock detail/history replay builder를 별도 모듈로 분리한다.
- `RealResearchProvider`에 남아 있던 도달 불가능한 v1 본문과 중복 fallback을 제거한다.
- develop 반영 전 필수 검증 게이트를 통과시킨다.

완료 조건
- `stock_builders.py`, `history_builders.py`와 전용 smoke 테스트가 추가된다.
- `RealResearchProvider`는 stock/history 화면 조립을 새 builder 함수로 위임한다.
- `pnpm verify:automation`과 `pnpm verify:standard`가 통과한다.
- develop 대상 PR을 생성하고 checks를 확인한다.
