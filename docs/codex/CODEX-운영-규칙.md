# Codex 운영 규칙

## 1. Codex에게 계속 기억시키는 정보의 위치
- 작업 규칙: `AGENTS.md`
- 구조 기억: `docs/architecture/*.yaml`
- 디자인 기억: `docs/design/design-memory.md`
- 변경 역사: `docs/changes/CHANGELOG_APPEND_ONLY.md`
- 큰 결정: `docs/adr/*.md`

## 2. 한 작업이 끝날 때 자동으로 같이 해야 하는 일
- 관련 manifest 업데이트
- design-memory 확인
- changelog append
- 필요 시 ADR 추가

## 3. 프롬프트 기본 형식
- 목표
- 참고 문서
- 제약
- 완료 조건

## 4. Codex가 해선 안 되는 것
- 사용자가 정의한 4페이지 구조를 임의로 재편
- 문서 삭제 또는 과거 결정 덮어쓰기
- 근거 없는 수치/뉴스/점수 생성
