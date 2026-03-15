공통 응답 계약:
- asOf: ISO datetime 문자열
- sourceRefs: 배열
- missingData: 배열
- confidence: 0~1
- facts: 사실 목록
- interpretation: 해석 목록
- risks: 리스크 목록

반드시:
- JSON schema를 따를 것
- null 대신 가능한 명시적 빈 배열/빈 문자열을 우선 고려할 것
- 입력에 없는 숫자를 생성하지 말 것
