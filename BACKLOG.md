# 자율 작업 백로그

이 문서는 AGENTS.md의 장기 목표를 현재 코드/서비스 상태에 맞는 실행 단위로 쪼갠 우선순위 목록이다.

## P0
- [ ] Render API의 `/overview`, `/radar` 초기 타임아웃 또는 느린 응답 원인을 줄이고, 연속 재검증에서 안정화한다.
- [ ] Discord 회의형 루프를 실제 사용자 메시지 기준으로 다시 한 번 end-to-end 검증하고, 역할 간 한국어 대화 흐름과 superseded 처리 결과를 저널에 남긴다.
- [ ] 현재 로컬 자동화 변경분을 issue-linked branch로 정리해 GitHub 자동 issue/branch/PR 흐름이 다시 막히지 않게 만든다.
- [ ] 프런트 `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar` 와 백엔드 대응 엔드포인트를 배포 환경에서 다시 점검하고 결과를 상태 파일에 반영한다.

## P1
- [ ] `calendar` 첫 요청 지연을 줄이기 위해 백엔드 fetch 순서, soft timeout, 캐시 가능 지점을 점검한다.
- [ ] `overview` / `radar` 에서 fallback reason, missingData, unavailable 표현이 실제 사용자 판단에 충분한지 다듬는다.
- [ ] Discord 운영 루프의 GitHub 자동화에 사람 리뷰 코멘트 재수집과 같은 PR 반영 흐름을 추가한다.
- [ ] 배포 readiness, 실제 서비스 smoke, main 반영 결과를 하나의 릴리스 체크 문서로 묶는다.

## P2
- [ ] 종목 상세의 차트/이벤트/규칙 preset 흐름을 더 강하게 연결해 실제 리서치 작업성이 올라가게 한다.
- [ ] 뉴스, 공시, 캘린더를 종목/섹터/시황 관점으로 엮는 후속 인텔리전스 화면을 검토한다.
- [ ] 운영 로그와 저널에서 한글 깨짐, 오래된 상태 파일, 잘못된 성공 판정을 자동 감지하는 guard를 추가한다.
