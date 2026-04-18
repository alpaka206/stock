1. `apps/web/lib/server/research-api.ts`에서 `[::1]` 을 local hostname 으로 인식하도록 최소 수정한다.
2. `[::1]` 케이스를 재현하는 회귀 테스트 1건을 추가하고 기존 검증 명령에 연결한다.
3. `pnpm lint:web` 와 관련 테스트/타입체크를 실행해 #134 범위만 회귀 여부를 확인한다.
4. 검증이 끝나면 `issue/134-research-api-ipv6-loopback -> develop_loop` PR을 만든다.
