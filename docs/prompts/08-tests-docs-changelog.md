# 08. Tests, Docs, Changelog

## 목표

구현한 변경이 실제 화면, API, 문서, 검증 명령 기준으로 설명 가능한 상태인지 확인한다.

## 확인 대상

- `pnpm verify:standard`
- 필요 시 `pnpm verify:web`, `pnpm verify:release`, `pnpm test:e2e`
- `README.md`
- `docs/architecture/page-manifest.yaml`
- `docs/architecture/component-manifest.yaml`
- `docs/design/design-memory.md`
- `docs/api-integration.md`
- `docs/deployment.md`

## 제약

- 검증 실패를 숨기지 않는다.
- 환경 변수, 토큰, 비밀 URL은 커밋하지 않는다.
- 대체 데이터가 사용자 화면에 노출되면 `(목데이터)` 표시가 있어야 한다.

## 완료 조건

- 변경 범위와 검증 결과가 한국어로 정리되어 있다.
- PR 본문에 테스트 결과와 남은 리스크가 포함되어 있다.
- 보안상 커밋하면 안 되는 파일이 포함되지 않았음을 확인했다.
