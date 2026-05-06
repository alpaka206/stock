1. `develop` 최신 상태에서 #160 후속 브랜치를 만든다.
2. stock detail builder와 history replay builder를 별도 모듈로 분리한다.
3. `RealResearchProvider`의 unreachable v1 code를 제거한다.
4. `pnpm smoke:api`, `pnpm verify:standard`, `pnpm verify:automation`을 실행한다.
5. 통과하면 `develop` 대상 PR을 생성하고 checks를 확인한다.
