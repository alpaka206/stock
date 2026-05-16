# 현재 상태

## 현재 사실

- 기준 브랜치: `develop`
- 현재 문서 보강 브랜치: `docs/189-backend-spring-plan`
- 관련 이슈: #189 `UI/UX 리디자인 및 자동화 제거`
- `main`은 배포 트리거 브랜치이므로 자주 병합하지 않는다. `develop`에 변경을 모은 뒤 사용자가 요청한 릴리스 묶음 단위로만 `develop -> main` PR을 연다.
- GitHub 저장소 설정에서 squash merge는 비활성화했다.
- `main` 브랜치 보호 규칙을 적용했다. force push와 branch deletion은 금지되고, PR에는 `verify`, `release-guard`, `dependency-review`, `codeql (javascript-typescript)`, `codeql (python)` 체크가 필요하다.
- `develop` 브랜치를 최신 `main` 기준으로 복구했고 보호 규칙을 적용했다. force push와 branch deletion은 금지되고, PR에는 `verify`, `dependency-review`, `codeql (javascript-typescript)`, `codeql (python)` 체크가 필요하다.
- merge 후 branch 자동 삭제는 비활성화했다.
- Dependabot security updates, vulnerability alerts, secret scanning, push protection은 활성 상태다.
- 핵심 화면은 `/overview`, `/radar`, `/stocks/[symbol]`, `/history` 기준으로 재정리 중이다.
- 뉴스와 일정 보조 화면도 깨진 문구를 제거하고 사용자용 문장으로 교체했다.
- 서버 저장이 필요한 리서치 스냅샷은 Next API와 FastAPI 저장소를 통해 관리하도록 변경했다.
- FastAPI 스냅샷 저장소는 `DATABASE_URL`이 있으면 Postgres를 사용하고, 없으면 로컬 JSON fallback을 사용한다.
- Docker Compose에는 Postgres, FastAPI, Next.js 웹 서비스를 포함했다.
- 무한 루프 자동화 파일과 검증 경로는 제거했다.
- Dependabot은 `develop` 대상과 그룹 업데이트 방식으로 정리했다.
- 메인 백엔드는 Spring Boot 기반 별도 저장소 `alpaka206/stock_BE`로 진행한다. Next.js는 화면/BFF, Python/FastAPI는 필요 시 데이터·AI·미디어 worker로 분리한다.
- `stock_BE`는 Spring Boot 3, Java 17, Postgres, Flyway, JPA 기반으로 초기화했고 `develop`을 기본 브랜치로 설정했다.
- `stock_BE`에는 종목, 가격 바, 원천 자료, 판단 기록, 리포트 예약, 구독 플랜, 미디어 자료, 더빙 작업 상태를 저장하는 1차 DB 모델을 추가했다.
- `stock_BE`의 `main`/`develop` 보호, squash merge 비활성화, branch 자동 삭제 비활성화, Dependabot security updates, secret scanning, push protection을 적용했다.

## 최근 검증 결과

- `pnpm guard:no-secrets` 통과.
- `node scripts/run-python.mjs scripts/text_quality_guard.py` 통과.
- `pnpm verify:standard` 통과.
- `pnpm test:e2e` 통과. 핵심 화면 4개와 레이더 이동, 종목 차트/패턴, 스냅샷 저장, 히스토리 재생을 확인했다.
- `pnpm audit --audit-level low` 통과.
- `pnpm --dir apps/web audit --audit-level low` 통과.
- PR #193은 배포 빈도를 낮추기 위해 병합하지 않고 닫았다. 문서 보강 변경은 `develop`에 누적된 상태다.
- `stock_BE`에서 `./mvnw.cmd test` 통과. PR #3 `ci: Maven wrapper 실행 권한 보강`은 checks 통과 후 merge commit 방식으로 `develop`에 반영했다.

## 남은 리스크

- 실제 데이터 API 키가 없는 환경에서는 fallback 데이터가 보이며, 사용자 화면에는 `(목데이터)`로 표시해야 한다.
- 대규모 UI 교체 후 표준 검증과 e2e는 통과했지만, 실제 배포 환경의 API 키와 캐시 정책은 별도 점검이 필요하다.
- 기존 Dependabot PR은 통합 PR로 대체하고 닫았다.
- 프런트는 아직 기존 FastAPI/Next API 계약을 사용한다. Spring Boot 백엔드 저장 뷰 API와 프런트 adapter 연결이 다음 큰 작업이다.

## 다음 우선순위

1. 남은 깨진 텍스트와 자동화 잔여 참조를 스캔한다.
2. `pnpm verify:standard`를 실행하고 실패를 고친다.
3. 배포가 필요한 시점에만 `develop -> main` release PR을 만들고, 그 전까지는 `develop`에 변경을 누적한다.
4. 실제 배포 환경에서 API 키, 캐시 정책, fallback 표시를 다시 점검한다.
5. Spring Boot 백엔드의 저장 뷰 API를 프런트 `RESEARCH_API_BASE_URL` 경로와 연결한다.
