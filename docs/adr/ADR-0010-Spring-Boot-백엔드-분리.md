# ADR-0010. Spring Boot 백엔드 분리

## 상태

채택

## 결정

운영 백엔드는 별도 저장소 `stock_BE`의 Spring Boot 서비스로 둔다. 이 프런트 저장소는 Next.js 화면, 서버 라우트, 공유 계약, 문서, 검증 스크립트를 관리한다.

## 이유

- 금융 데이터와 사용자 판단 기록은 서버 저장, 캐시, 출처 추적, 트랜잭션 처리가 중요하다.
- API 키, refresh token, provider rate limit은 백엔드에서 관리해야 한다.
- 로그인, 구독, 리포트 발송, Perso 더빙 작업은 장기적으로 관계형 데이터 모델과 보안 필터가 필요하다.

## 결과

- 프런트 기본 API URL은 `STOCK_API_BASE_URL=http://localhost:8080`이다.
- 백엔드는 `/v3/api-docs`, `/swagger-ui.html`로 Swagger 문서를 제공한다.
- 인증은 백엔드 `HttpOnly` access/refresh cookie 전략을 따른다.
- 프런트는 token 원문을 저장하지 않는다.
