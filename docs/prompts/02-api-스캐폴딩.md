# 목표

프런트 저장소는 Spring Boot 백엔드 `../stock_BE`와 연결되는 API adapter와 환경변수 계약을 정리한다.

# 참고 문서

- docs/api-integration.md
- docs/architecture/page-manifest.yaml
- ../stock_BE/README.md
- ../stock_BE/docs/architecture.md

# 할 일

- `STOCK_API_BASE_URL` 기본값을 Spring Boot 로컬 포트 `8080`으로 맞춘다.
- 화면 단위 route가 `/overview`, `/radar`, `/stocks/{symbol}`, `/history` 백엔드 응답을 우선 사용하도록 확인한다.
- snapshot mutation은 백엔드 `/csrf`를 거쳐 `POST /snapshots`, `DELETE /snapshots/{id}`로 전달한다.
- Swagger `/v3/api-docs`와 프런트 타입 차이를 점검한다.

# 제약

- 프런트에서 외부 금융 API 키를 직접 사용하지 않는다.
- token 원문을 localStorage/sessionStorage에 저장하지 않는다.
- fallback 데이터가 노출되면 `(목데이터)`를 표시한다.

# 완료 조건

- Spring Boot 백엔드가 켜진 상태에서 핵심 화면 API가 응답한다.
- `pnpm verify:standard`가 통과한다.
- 필요한 백엔드 변경은 `stock_BE` PR로 별도 반영된다.
