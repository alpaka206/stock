# STATE

## 현재 사실

- 저장소 목적은 미국 주식과 한국 주식을 함께 지원하는 주식 리서치 워크스페이스 구축이다.
- 핵심 화면은 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 이다.
- Discord bridge 와 GitHub 자동 흐름은 최소 종료 조건의 일부다.
- Git 흐름은 `main -> develop -> issue branch -> develop -> main` 이다.
- issue branch -> `develop` PR 은 green 이면 자동 merge 대상이다.
- `develop -> main` PR 은 자동 생성하되 최종 merge 는 사용자가 직접 수행한다.
- 루프 1번째 시작에서는 한 명의 agent만 Discord에 `작업을 시작합니다.` 를 전송해야 한다.

## 최근 검증

- 최근 실행 명령:
- 결과:
- 확인한 화면:
- 확인한 API:
- Discord 운영 검증:
- GitHub 흐름 검증:

## 현재 리스크

- `/overview` 초기 지연 원인 미확정
- `/radar` 초기 지연 원인 미확정
- Discord latest-only 처리 실물 검증 필요
- `develop -> main` PR 생성 후 Discord 보고 자동화 검증 필요
- 미국/한국 주식 통합 검색 및 공시/뉴스 데이터 품질 검증 필요
- 차트 보조지표와 이동평균선 UX 완성도 검증 필요
- 어닝콜/연준 발표 등 오디오 자료 수집 경로와 저장 규칙 미정

## 다음 우선순위

1. 실제 Discord 메시지 1건으로 ingest -> 회의 -> 회신 -> 로그 기록까지 검증
2. `/overview`, `/radar` 초기 지연 재현 후 원인 축소
3. `pnpm verify:automation` / `pnpm verify:standard` 통과 복구
4. issue 생성, 브랜치 생성, PR 자동 흐름 재개
5. 결과를 저널과 상태 문서에 한국어로 기록

## 참고 메모

- `omx_discord_bridge/.env.discord` 는 읽기 전용 비밀 입력으로만 다룬다.
- 출처 없는 가격, 뉴스, 점수, 레벨은 만들지 않는다.
- 한글 문서 저장 전 한글 깨짐, 이중 물음표, raw unicode escape 여부를 확인한다.
