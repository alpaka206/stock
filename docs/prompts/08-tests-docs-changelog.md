# 목표

구현 완료 직후 검증, 문서, 상태 기록을 한 번에 마무리한다.

# 함께 갱신할 문서

- `README.md`
- `apps/web/README.md`
- `apps/api/README.md`
- `docs/adr/`
- `.omx/state/TASK.md`
- `.omx/state/STATE.md`
- `.omx/state/BACKLOG.md`
- `.omx/state/DISCORD_STATUS.md`
- `.omx/state/VERIFY_LAST_FAILURE.md`

# 검증

- web lint / typecheck / build를 실행한다.
- api smoke / workspace verify를 실행한다.
- README, ADR, `docs/codex/prompt-order.md`, OMX 상태 파일을 실제 구현 상태에 맞게 갱신한다.
- `.omx/journal/loop-*.md`에 이번 iteration의 작업, 검증, 다음 액션을 남긴다.

# 완료 조건

- web과 api 검증 결과가 남아 있다.
- 문서와 상태 파일이 실제 구현 상태와 일치한다.
- ADR 또는 OMX 상태 기록이 필요한 변경이 누락되지 않았다.
