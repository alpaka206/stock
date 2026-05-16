# ADR-0005. 실데이터 및 LLM provider 선택

## 상태

대체됨. 현재 구조는 ADR-0010을 따른다.

## 메모

외부 금융 API, LLM provider, Perso 작업은 프런트가 직접 호출하지 않는다. 서버에서 키와 rate limit, 저장, 출처 추적을 관리하고 프런트는 백엔드 API 응답을 사용한다.
