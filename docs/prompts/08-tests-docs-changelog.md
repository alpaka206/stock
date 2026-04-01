# 목표
최종 검증과 릴리즈 마감 문서를 정리한다.

# 참고 문서
- README.md
- apps/web/README.md
- apps/api/README.md
- docs/changes/CHANGELOG_APPEND_ONLY.md
- docs/adr/

# 할 일
- web lint / typecheck / build를 실행한다.
- api py_compile과 TestClient smoke test를 실행한다.
- README 실행 경로를 실제 구조와 맞춘다.
- changelog를 append-only로 추가한다.
- 필요하면 ADR을 추가한다.
- prompt-order와 실제 prompt 문서 경로를 맞춘다.

# 완료 조건
- mock 모드 기준 web과 api가 검증된다.
- 실행 문서가 실제 명령과 맞는다.
- changelog와 ADR이 누락 없이 정리된다.
