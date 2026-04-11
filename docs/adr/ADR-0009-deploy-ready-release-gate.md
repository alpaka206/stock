# ADR-0009: Deploy-ready release gate 도입

- Status: Approved
- Date: 2026-04-09

## Background

저장소는 이미 `pnpm verify:standard`를 통해 개발 회귀 검증을 수행하고 있었지만, 실제 배포 직전 품질 게이트는 없었다.

- web은 API 미설정/오류 시 fixture fallback 경로를 갖고 있었다.
- API는 `/health`만 있었고, real provider 3종 정상 여부를 한 번에 판정하는 readiness 경로가 없었다.
- 사용자는 배포 승인 기준을 **Alpha Vantage + OpenDART + OpenAI 3종 모두 정상**으로 명시했다.

## Decision

- 표준 개발 게이트와 릴리스 게이트를 분리한다.
- 릴리스 게이트 명령으로 `pnpm verify:release` / `pnpm verify:release:json`를 추가한다.
- API는 `/health`와 별도로 `/readyz`를 제공한다.
  - `probe=config`
  - `probe=remote`
- production 후보에서는 `RESEARCH_ALLOW_FIXTURE_FALLBACK=false`를 강제하고, API URL 미설정 상태를 fixture로 숨기지 않는다.
- API 배포 템플릿으로 `apps/api/Dockerfile`을 추가한다.

## Why

- 개발 편의용 fallback과 실배포 승인 기준을 분리해야 silent degradation을 막을 수 있다.
- 실 provider 3종을 명시적으로 probe해야 “실제 값 기반 배포 가능 상태”를 증명할 수 있다.
- 실제 배포 실행은 범위 밖이지만, deploy-ready 상태를 코드/문서/검증 명령으로 고정할 필요가 있다.

## Impact

- root `package.json`에 릴리스 검증 스크립트가 추가된다.
- API는 `/readyz`를 통해 config probe와 remote probe를 분리해 노출한다.
- web loader는 production 후보에서 API URL 미설정을 fixture로 숨기지 않는다.
- docs/deployment, docs/api-integration, docs/env-checklist, docs/test-strategy, app READMEs가 새 게이트를 기준으로 갱신된다.
