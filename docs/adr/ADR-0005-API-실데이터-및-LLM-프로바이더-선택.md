# ADR-0005: API 실데이터 및 LLM provider 선택

## 상태
승인

## 맥락
`apps/api` 는 화면 단위 endpoint 구조를 이미 갖췄지만, 실제 시장 데이터와 요약 LLM 호출은 비어 있었다.  
초기 단계에서는 유료 데이터 라이선스를 전제하지 않고, 동시에 sourceRefs 추적이 가능한 구조가 필요하다.

## 결정
- 실데이터 provider 는 Alpha Vantage 를 기본값으로 사용한다.
- LLM 요약 provider 는 OpenAI Responses API structured output 을 사용한다.
- 수치/시계열/fundamentals 는 deterministic facts 로 먼저 수집한다.
- LLM 은 facts 기반 해석과 한국어 요약만 담당한다.
- 모든 분석 응답은 고정된 `sourceRefs` 계약과 `missingData`, `confidence` 구조를 가진다.

## 이유
- Alpha Vantage 는 무료 플랜으로 시세, 시계열, 뉴스 sentiment, 기업 overview, 일부 경제지표를 한 API 계열에서 가져올 수 있다.
- OpenAI structured output 을 사용하면 페이지별 JSON schema 와 응답 계약을 맞추기 쉽다.
- facts 와 interpretation 을 분리하면 금융 리서치 특성상 추적성과 방어적인 오류 처리가 쉬워진다.

## 결과
- `real provider` 는 API key 기반으로 즉시 연결 가능하다.
- 옵션/공매도/기관수급처럼 아직 미연결인 데이터는 `missingData` 로 드러난다.
- 프론트엔드는 고정된 envelope 구조를 기준으로 서버 상태를 붙일 수 있다.
