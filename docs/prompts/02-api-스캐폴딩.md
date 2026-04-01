# 목표
`apps/api`를 화면 단위 endpoint와 런타임 프롬프트 로더를 가진 구조로 스캐폴딩한다.

# 참고 문서
- apps/api/AGENTS.md
- docs/architecture/page-manifest.yaml

# 할 일
- FastAPI app entry를 만든다.
- 화면 단위 router를 만든다.
  - overview
  - radar
  - stocks
  - history
- Pydantic schema 디렉터리를 만든다.
- 프롬프트 로더 유틸과 JSON schema validator 구조를 만든다.
- mock provider와 real provider interface를 분리한다.

# 제약
- 응답 모델은 반드시 타입으로 선언한다.
- 분석 응답에는 `asOf`, `sourceRefs`, `missingData`, `confidence` 구조를 고려한다.
- 프롬프트 문자열을 코드에 하드코딩하지 않는다.

# 완료 조건
- FastAPI 서버가 부팅된다.
- 4개 화면용 기본 endpoint가 응답한다.
- prompt loader가 파일을 읽어온다.
- schema validation 흐름이 준비된다.
