# Contributing Quick Guide

## 작업 흐름

1. 이슈 생성
2. `develop_loop` 기준 작업 브랜치 생성
3. 검증 통과
4. `develop_loop` 대상 PR
5. 안정화 후 `develop`
6. 릴리스는 `develop -> main`

## 필수 확인

- `pnpm verify:standard`
- `pnpm verify:automation`
- UI 변경 설명 또는 스크린샷
- 리스크와 후속 작업 정리
