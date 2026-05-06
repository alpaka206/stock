현재 사실
- `develop` 최신 커밋 `019b4e4` 기준으로 브랜치 `issue/162-disclosure-sources`에서 작업 중이다.
- `SecFilingsClient`가 `https://data.sec.gov/submissions/CIK##########.json`에서 최근 filings를 읽고 주요 form만 추린다.
- 기본 CIK 매핑은 NVDA, AMD, AVGO, MSFT, CRWD를 포함하며 `SEC_SYMBOL_CIKS`로 바꿀 수 있다.
- SEC 요청 User-Agent는 `SEC_USER_AGENT`로 설정하며 기본값은 개발용 contact 문자열이다.
- `/news`는 기존 해외 뉴스 뒤에 SEC filing 카드를 글로벌 feed로 병합한다.
- `/calendar`는 IPO 이벤트와 SEC filing 이벤트를 함께 market events로 제공한다.

최근 검증 결과
- `node scripts/run-python.mjs scripts/test_sec_filings_client.py`: 통과.
- `pnpm smoke:api`: 통과.
- `pnpm test:e2e -- --project=chromium`: 8개 시나리오 통과.
- `pnpm verify:automation`: 통과.
- `pnpm verify:standard`: 통과.
- 표준 검증 안에서 SEC filings client, API py_compile, API smoke가 모두 통과했다.

남은 리스크
- SEC CIK 매핑은 현재 watchlist 기본 종목 중심의 정적 매핑이다.
- SEC API는 User-Agent 정책을 요구하므로 배포 환경에서는 실제 연락 가능한 값을 설정해야 한다.
- `/stocks/[symbol]` 상세 화면의 개별 filing 카드까지는 아직 확장하지 않았다.

다음 우선순위
- 현재 변경사항을 `feat: 미국 SEC 공시 데이터 소스 추가` 커밋으로 정리한다.
- 브랜치를 원격에 push하고 `develop` 대상 PR을 생성한다.
- PR checks 통과 후 auto-merge를 설정한다.
- 다음 브랜치에서는 이슈 #163 관심종목 알림과 조건 감지 워크플로를 구현한다.
