# 현재 상태

2026-04-12 기준으로 로컬 코드와 검증 게이트는 복구됐다.

- Discord bridge는 `/health`, `/sync-replies`, `/event` 응답이 정상이며, 최신 사용자 지시 1건만 회의 트리거로 사용하고 이전 지시는 superseded로 정리한다.
- `scripts/text_quality_guard.py`가 통과하며, 핵심 상태 파일과 코드 경로에서 이중 물음표 플레이스홀더·raw unicode escape·한글 깨짐을 계속 감시한다.
- API는 `/overview`, `/radar`, `/stocks/NVDA`, `/history`, `/news`, `/calendar` 전부 로컬 smoke와 release gate에서 200을 반환한다.
- Alpha Vantage 일일 쿼터가 소진돼도 Yahoo Finance 백업 경로로 radar/history/stock detail 시계열을 유지한다.
- 남은 blocker는 원격 배포 환경이다. 현재 `https://stock-9i67.onrender.com` 는 `/news`만 200이고 나머지 주요 라우트는 5xx라서, main 반영과 원격 재배포 없이는 배포 사이트 FE/BE 직접 확인을 완료할 수 없다.
