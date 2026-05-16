# 현재 상태

## 현재 사실

- 기준 브랜치: `develop`
- 현재 문서 보강 브랜치: `docs/189-release-cadence`
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

## 최근 검증 결과

- `pnpm guard:no-secrets` 통과.
- `node scripts/run-python.mjs scripts/text_quality_guard.py` 통과.
- `pnpm verify:standard` 통과.
- `pnpm test:e2e` 통과. 핵심 화면 4개와 레이더 이동, 종목 차트/패턴, 스냅샷 저장, 히스토리 재생을 확인했다.
- `pnpm audit --audit-level low` 통과.
- `pnpm --dir apps/web audit --audit-level low` 통과.
- PR #193은 배포 빈도를 낮추기 위해 병합하지 않고 닫았다. 문서 보강 변경은 `develop`에 누적된 상태다.

## 남은 리스크

- 실제 데이터 API 키가 없는 환경에서는 fallback 데이터가 보이며, 사용자 화면에는 `(목데이터)`로 표시해야 한다.
- 대규모 UI 교체 후 표준 검증과 e2e는 통과했지만, 실제 배포 환경의 API 키와 캐시 정책은 별도 점검이 필요하다.
- 기존 Dependabot PR은 통합 PR로 대체하고 닫았다.
- `alpaka206/stock_BE`는 현재 비어 있어 백엔드 분리는 별도 초기화 작업이 필요하다.

## 다음 우선순위

1. 남은 깨진 텍스트와 자동화 잔여 참조를 스캔한다.
2. `pnpm verify:standard`를 실행하고 실패를 고친다.
3. 배포가 필요한 시점에만 `develop -> main` release PR을 만들고, 그 전까지는 `develop`에 변경을 누적한다.
4. 실제 배포 환경에서 API 키, 캐시 정책, fallback 표시를 다시 점검한다.
