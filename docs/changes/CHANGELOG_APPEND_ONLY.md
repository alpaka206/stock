# CHANGELOG (Append Only)

## 2026-03-15 13:00 KST
### 추가
- 4개 메인 페이지 중심 IA 정의
- 루트/웹/API 3개의 AGENTS.md 초안 추가
- Codex 프롬프트 순서 문서 추가
- 페이지/컴포넌트 manifest 추가
- 디자인 메모리 문서 추가
- 런타임 AI 프롬프트 디렉터리 구조 추가

### 이유
- 사용자가 4개 화면 구조를 반복 설명하지 않아도 Codex가 지속적으로 참조할 수 있게 하기 위해
- 추후 구조 변경 시 "무엇이 바뀌었는지"와 "왜 바꿨는지"가 누적되도록 하기 위해

### 영향
- 이후 구현 작업은 AGENTS.md + manifest + design-memory를 먼저 읽는 방식으로 진행해야 함

## 2026-03-15 - 무료 그리드 전략으로 조정
- 무엇을: AG Grid 전제를 AG Grid Community 기준으로 명확화하고 Enterprise 의존 문구를 제거했다.
- 왜: 초기 단계에서는 유료 라이선스 비용을 쓰지 않기로 결정했기 때문이다.
- 어떻게: README, 루트/웹 AGENTS, manifest를 갱신하고 ADR-0003을 추가했다.
- 영향 범위: `/radar` grid 구현 방식, 컬럼 토글 UX, 그룹 뷰 구조, Codex 프롬프트 기본 방향
