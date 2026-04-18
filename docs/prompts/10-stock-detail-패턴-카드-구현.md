# 목표
`stocks/[symbol]` 화면에 패턴 도감 카드와 현재 유사 패턴 패널을 구현한다.

# 반드시 읽을 문서
- docs/design/stock-reference-blueprint.md
- docs/design/chart-pattern-atlas.md
- docs/prompts/09-완성형-주식-분석-사이트.md
- docs/architecture/component-manifest.yaml

# 구현 목표
- 차트 옆 또는 아래에 패턴 도감 카드 영역을 추가한다.
- 대표 패턴을 이미지 또는 단순 도식 카드로 보여준다.
- 현재 종목 차트와 가장 유사한 패턴 1개에서 3개를 별도 패널로 보여준다.
- "지금 이런 차트로 진행 중이에요" 수준으로 한국어 설명을 제공한다.

# 필수 요소
- 대표 패턴 카드:
  - cup with handle
  - double bottom
  - saucer base
  - flat base
  - ascending base
- 현재 유사 패턴 패널:
  - 패턴 이름
  - 유사 이유
  - 현재 단계
  - 무효화 조건
  - 주의 포인트

# 문구 원칙
- 투자 조언처럼 단정하지 말 것
- "관찰 구간", "지지 확인 필요", "돌파 전 확인 필요", "무효화 주의" 같은 표현 사용
- 초보자도 읽을 수 있는 쉬운 한국어 우선

# 완료 조건
- stock detail에서 차트와 패턴 카드가 함께 보인다
- 현재 유사 패턴 패널이 실제 데이터와 연결된다
- 디자인이 카드 나열 수준이 아니라 연구 도구처럼 보인다
