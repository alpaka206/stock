# ADR-0009. 릴리스 검증 게이트

## 상태

업데이트됨. 현재 구조는 ADR-0010과 함께 적용한다.

## 결정

프런트 릴리스 검증은 `pnpm verify:standard`와 `pnpm verify:release`를 사용한다. `verify:release`는 실행 중인 Spring Boot 백엔드의 readiness, OpenAPI 문서, 핵심 화면 API를 HTTP로 확인한다.
