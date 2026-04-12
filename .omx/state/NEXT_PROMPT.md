# 다음 작업 지침

현재 최소 종료 조건은 충족했다. 다음 세션에서는 아래 순서로 이어가면 된다.

1. `stock-mu-seven.vercel.app` 와 `stock-9i67.onrender.com` 의 핵심 경로를 다시 한 번 빠르게 점검한다.
2. `calendar` 첫 요청 지연 원인을 백엔드 기준으로 더 줄일 수 있는지 본다.
3. 깨진 한글이나 잘못 인코딩된 문자열이 남아 있는 코드와 문서를 저장소 전반에서 추가 정리한다.
4. Discord 회의형 루프, 주식 데이터 흐름, 배포 검증 결과를 기준으로 후속 가치가 높은 기능을 고른다.

## 재확인할 기준 경로

- 프런트: `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar`
- 백엔드: `/overview`, `/radar`, `/stocks/NVDA`, `/history?symbol=NVDA`, `/news`, `/calendar`
