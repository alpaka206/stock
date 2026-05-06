# Overview Redesign Audit

## 목적

`/overview` 첫 화면이 범용 대시보드처럼 보이는 문제를 줄이고, 주식 리서치 데스크의 실제 작업 화면처럼 보이도록 조정한다.

## 확인한 문제

- `AI Research`, `Stock Workspace`처럼 제품 성격보다 생성형 도구 느낌이 강한 문구가 많았다.
- 카드 패턴이 반복되어 지수, 뉴스, 섹터, 리스크의 정보 성격이 잘 구분되지 않았다.
- 헤더가 설명형 랜딩 페이지처럼 보여 사용자가 먼저 봐야 할 장 상태와 데이터 상태가 뒤로 밀렸다.
- 한국어와 영어가 섞인 문구가 남아 있어 금융 리서치 제품의 신뢰감이 약했다.

## 적용 방향

- 공통 shell은 `주식 리서치 데스크` 톤으로 정리한다.
- `/overview`는 장 상태, 최종 업데이트, 데이터 상태를 가장 먼저 보여준다.
- 오프닝 브리프, 핵심 지수 스트립, 섹터 플로우, 헤드라인 플로우, 리스크 체크를 서로 다른 정보 밀도로 배치한다.
- AI라는 표현은 전면 카피에서 줄이고, 사용자가 읽는 결과와 근거를 먼저 보이게 한다.

## 이번 변경 대상

- `apps/web/app/globals.css`
- `apps/web/lib/tokens.ts`
- `apps/web/components/shell/*`
- `apps/web/features/overview/components/*`
- `apps/web/lib/i18n/messages.ts`

## 남은 점검

- 실제 브라우저에서 `/overview` 데스크톱과 모바일 첫 화면을 스크린샷 기준으로 확인한다.
- 같은 패널 언어와 밀도를 `/radar`, `/stocks/[symbol]`, `/history`에도 이어서 적용한다.
- 배포 환경에서 데이터 fallback 표시와 리스크 문구가 과하게 보이지 않는지 확인한다.
