# 현재 라운드 목표

UI/UX 리디자인, 성능 개선, 서버 저장 구조, 자동화 제거, Dependabot 정리를 하나의 issue branch에서 검증 가능한 상태로 만든다.

## 완료 조건

- `/overview`, `/radar`, `/stocks/[symbol]`, `/history`가 새 디자인으로 빌드된다.
- 뉴스, 일정, 스냅샷 fallback 데이터는 `(목데이터)`로 표시된다.
- 무한 루프 자동화 파일과 검증 경로가 제거된다.
- Dependabot 대상 브랜치와 그룹 설정이 `develop` 기준으로 정리된다.
- `pnpm verify:standard` 결과가 기록된다.
