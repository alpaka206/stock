# 백로그

## P0
- [ ] Discord bridge와 OMX loop가 최신 Discord 사용자 지시 1건만 소비하고 이전 미처리 지시는 superseded로 정리한다.
- [ ] `planner -> critic -> researcher -> architect -> executor -> verifier` 회의 흐름이 실제 Discord와 `.omx/state/TEAM_CONVERSATION.jsonl`에 남는다.
- [ ] 중요한 Discord 사용자 지시를 `.omx/state/DISCORD_IMPORTANT.md`에 한국어로 정리한다.
- [ ] `scripts/text_quality_guard.py`와 핵심 상태 파일·프롬프트·루프 스크립트에서 이중 물음표 플레이스홀더, raw unicode escape, 한글 깨짐을 제거한다.

## P1
- [ ] `/overview`, `/radar`, `/stocks/[symbol]`, `/history`의 API·FE·BE 연결을 점검하고 누락 기능을 채운다.
- [ ] 차트, 글로벌 뉴스, 공시, 스코어링, 검색, preset, history replay를 end-to-end로 검증한다.
- [ ] executor 이후 `scripts/no_secrets_guard.sh`와 `scripts/verify_minimal.sh`를 자동 실행하고 실패를 복구한다.

## P2
- [ ] QA, release gate, main 반영, 배포, 배포 사이트 실측 검증을 완료한다.
- [ ] 유용한 후속 기능과 추가 점검 결과를 문서와 저널에 남긴다.
