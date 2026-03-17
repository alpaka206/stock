공통 응답 계약:
- `asOf`: ISO datetime 문자열
- `sourceRefs`: 고유 출처 배열
- `missingData`: `{ field, reason, expectedSource }` 배열
- `confidence`: `{ score, label, rationale }`

세부 규칙:
- `score`는 0~1 범위여야 한다.
- `label`은 `low`, `medium`, `high` 중 하나여야 한다.
- 설명형 필드가 object로 선언돼 있으면 `{ text, sourceRefIds }` 구조를 사용한다.
- 숫자나 사실을 만들지 않는다.
- 데이터가 없으면 추정하지 말고 `missingData`를 반영한 보수적 문장을 쓴다.
- 한국어로만 작성한다.
