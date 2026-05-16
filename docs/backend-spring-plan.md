# Spring Boot 백엔드 전환 계획

## 결정

메인 백엔드는 `alpaka206/stock_BE`의 Spring Boot 서비스로 둔다. Next.js는 화면과 얇은 BFF 역할을 유지하고, 외부 금융 API와 Perso, LLM, 이메일, 결제 같은 서버 관리 값은 백엔드가 저장·관리한다.

## 이유

- 주식 리서치 서비스는 가격·뉴스·공시를 빠르게 보여주는 화면보다 저장소 품질이 더 중요하다.
- 프런트가 외부 API를 직접 호출하면 API 키 노출, rate limit, 장애 대응, 캐시, 출처 추적이 모두 약해진다.
- Spring Boot는 DB 트랜잭션, Flyway migration, JPA 관계 모델, 보안 필터, 관측성, 결제·구독·메일 연동을 장기 운영 구조로 잡기 좋다.
- Python/FastAPI는 버리는 것이 아니라, 필요 시 데이터 수집·LLM 요약·Perso 더빙 worker로 분리한다.

## 목표 구조

```text
외부 API / 수집 worker
  -> Spring Boot 백엔드 저장소
  -> Postgres / Redis
  -> Next.js BFF
  -> 사용자 화면
```

## 백엔드 저장 대상

- 종목 기본 정보
- 일별 가격 바
- 뉴스, 공시, 실적, 연준 발표, 경제 지표 원문
- 사용자 판단 기록
- 구독 플랜과 기능 제한 정의
- 오늘/이번주 리포트 발송 예약
- 어닝콜·연준 발표 오디오/영상 자료
- Perso 더빙·자막 작업 상태

## 현재 백엔드 레포 상태

- 저장소: `https://github.com/alpaka206/stock_BE`
- 기준 브랜치: `develop`
- 메인 스택: Spring Boot 3, Java 17, Postgres, Flyway, JPA
- CI: `verify`, `dependency-review`, `codeql`
- GitHub 설정: squash merge 비활성화, branch 자동 삭제 비활성화, `main`/`develop` 보호 적용

## 남은 연동 작업

1. 프런트의 `RESEARCH_API_BASE_URL`을 Spring Boot API로 전환할 수 있게 adapter를 분리한다.
2. 기존 FastAPI 화면 응답 계약을 Spring Boot 저장 뷰 API로 재구성한다.
3. 외부 provider 호출 결과를 `source_materials`, `price_bars`에 저장하는 ingest worker를 붙인다.
4. 로그인 도입 후 `research_snapshots`, report schedule, subscription plan을 사용자 계정과 연결한다.
5. Perso API 계약 확정 후 `media_assets`, `localization_jobs`에 작업 생성·조회 API를 연결한다.
