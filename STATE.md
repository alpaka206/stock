현재 사실
- `develop` 최신 커밋 `4d68325` 기준으로 브랜치 `issue/161-research-snapshot-persistence`에서 작업 중이다.
- API에 `/snapshots` GET/POST/DELETE가 추가되었고 기본 저장 위치는 `.omx/runtime/research_snapshots.json`이다.
- `RESEARCH_SNAPSHOT_STORE_PATH`로 저장 파일 경로를 바꿀 수 있어 smoke 검증은 `.omx/tmp/api_smoke_snapshots.json`을 사용한다.
- 웹은 `/api/research-snapshots` 프록시를 통해 backend snapshots API와 동기화하고, API가 없거나 실패해도 기존 localStorage 저장 흐름을 유지한다.
- 종목 상세에서 저장한 스냅샷은 같은 브라우저 세션의 히스토리 화면에서 재확인된다.

최근 검증 결과
- `pnpm smoke:api`: `/snapshots` GET, POST, symbol filter GET, DELETE 통과.
- `pnpm test:e2e -- --project=chromium`: 8개 시나리오 통과.
- `pnpm verify:automation`: 통과.
- `pnpm verify:standard`: 통과.
- 표준 검증 안에서 web lint, typecheck, build, contract parity, API py_compile, API smoke가 모두 통과했다.

남은 리스크
- 현재 API 저장소는 단일 JSON 파일 기반이라 다중 사용자 동시 편집과 장기 백업 전략은 제한적이다.
- 인증이 없으므로 배포 공개 환경에서는 사용자별 스냅샷 분리나 보호가 필요하다.
- 실제 배포 API 저장 경로는 호스팅 환경의 쓰기 가능 파일시스템 여부를 확인해야 한다.

다음 우선순위
- 현재 변경사항을 `feat: 리서치 스냅샷 영속 저장소 구현` 커밋으로 정리한다.
- 브랜치를 원격에 push하고 `develop` 대상 PR을 생성한다.
- PR checks 통과 후 auto-merge를 설정한다.
- 다음 브랜치에서는 이슈 #162 한국/미국 공시 데이터 소스 확장을 진행한다.
