## 요약
-

## 변경 내용
-

## 사용자 영향
-

## 검증
- [ ] `pnpm verify:standard`
- [ ] `pnpm verify:release`
- [ ] 핵심 화면 직접 확인

## 보안 확인
- [ ] `.env`, `.env.*`, API 키, 토큰, 웹훅 URL 미포함
- [ ] 목데이터 또는 fallback 데이터는 화면에 `(목데이터)`로 표시
- [ ] 실제 데이터 API 오류와 누락 데이터 처리 확인
