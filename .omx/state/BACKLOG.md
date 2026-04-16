# 백로그

## P0
- [ ] 실제 Discord 채널에서 허용 사용자 메시지 1건으로 ingest -> 역할 회의 -> 회신 -> `.omx/state/TEAM_CONVERSATION.jsonl` 기록까지 실물 검증하고 결과를 `.omx/state/STATE.md` 와 `.omx/journal/` 에 남긴다.
- [ ] `/overview`, `/radar` 초기 응답 지연을 배포 환경 기준으로 다시 재현하고, 원인을 줄인 뒤 재검증 결과를 기록한다.
- [ ] `scripts/text_quality_guard.py` 와 핵심 상태 파일, 프롬프트, 루프 스크립트에서 이중 물음표 플레이스홀더, raw unicode escape, 한글 깨짐을 제거한다.

## P1
- [ ] 차트, 실시간 글로벌 뉴스, 공시, 스코어링, 검색 preset, history replay를 end-to-end 로 검증한다.
- [ ] issue-linked branch 기준 GitHub 자동 issue -> branch -> PR -> develop 흐름을 다시 연다.
- [ ] develop -> main release PR, release 검증, 배포 사이트 실측 확인까지 이어간다.

## P2
- [ ] 남은 리스크와 운영 메모를 한국어로 정리한다.
- [ ] 추가 가치가 높은 후속 기능을 선별하고 우선순위를 문서화한다.
