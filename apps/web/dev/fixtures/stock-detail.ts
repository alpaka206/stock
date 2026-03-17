import type { PricePoint, StockFixture } from "@/lib/research/types";

const baseChart: PricePoint[] = [
  { label: "03/01", close: 842, volume: 44 },
  { label: "03/03", close: 851, volume: 39 },
  { label: "03/05", close: 865, volume: 48 },
  { label: "03/07", close: 858, volume: 41 },
  { label: "03/09", close: 876, volume: 54 },
  { label: "03/11", close: 889, volume: 58 },
  { label: "03/13", close: 901, volume: 63 },
  { label: "03/15", close: 917, volume: 60 },
  { label: "03/16", close: 923, volume: 57 },
];

function scaleChart(points: PricePoint[], multiplier: number) {
  return points.map((point) => ({
    ...point,
    close: Number((point.close * multiplier).toFixed(2)),
  }));
}

export const stockFixtures: Record<string, StockFixture> = {
  NVDA: {
    symbol: "NVDA",
    name: "NVIDIA",
    exchange: "NASDAQ",
    price: 923.42,
    changePercent: 2.16,
    marketCap: "2.28T",
    thesis:
      "AI 서버 CAPEX 확대가 이어지는 동안 가장 강한 기준 종목이다. 다만 이벤트 전후 변동성이 크므로 가이던스 확인과 수급 지속 여부를 같이 본다.",
    chartPoints: baseChart,
    indicatorGuides: [
      { label: "지지 구간", value: 889, tone: "positive" },
      { label: "추세 기준선", value: 901, tone: "neutral" },
      { label: "단기 과열 경계", value: 938, tone: "negative" },
    ],
    rulePresets: [
      { label: "상대강도 80 이상 유지", description: "리더십 훼손 여부 체크", enabled: true },
      { label: "거래량 배수 1.2 이상", description: "추세 신뢰도 확인", enabled: true },
      { label: "지지선 889 이탈", description: "무효화 트리거", enabled: false },
    ],
    scoreBreakdown: [
      { label: "실적 가시성", score: 94, summary: "가이던스 상향 기대가 가장 높다." },
      { label: "수급 지속성", score: 89, summary: "기관 선호가 유지되고 있다." },
      { label: "밸류 부담", score: 61, summary: "고점 부근 추격 리스크는 남아 있다." },
    ],
    flows: [
      { label: "기관 수급", value: "+18.2억 달러", delta: "5일 연속 순유입", tone: "positive" },
      { label: "개인 수급", value: "-3.7억 달러", delta: "차익 실현 우세", tone: "neutral" },
      { label: "해외 수급", value: "+6.4억 달러", delta: "반도체 리더 선호", tone: "positive" },
    ],
    shortOptionMetrics: [
      { label: "콜/풋 비율", value: "1.48", detail: "상단 베팅 우세", tone: "positive" },
      { label: "공매도 비중", value: "1.2%", detail: "압박은 크지 않음", tone: "neutral" },
      { label: "암묵 변동성", value: "42%", detail: "이벤트 전 프리미엄 확대", tone: "negative" },
    ],
    issues: [
      {
        title: "패키징 공급 개선 코멘트",
        source: "공급망 메모",
        summary: "하반기 출하량 상향 가능성이 다시 거론되는 구간",
        tone: "positive",
      },
      {
        title: "이벤트 전 기대 과열",
        source: "리스크 메모",
        summary: "키노트 이후 재료 소멸이 나오면 변동성이 커질 수 있음",
        tone: "negative",
      },
    ],
    relatedSymbols: ["AVGO", "AMD", "VRT"],
  },
  AVGO: {
    symbol: "AVGO",
    name: "Broadcom",
    exchange: "NASDAQ",
    price: 1345.88,
    changePercent: 1.34,
    marketCap: "626B",
    thesis: "네트워크와 커스텀 AI칩 노출을 동시에 가진 고품질 바스켓.",
    chartPoints: scaleChart(baseChart, 1.45),
    indicatorGuides: [
      { label: "지지 구간", value: 1288, tone: "positive" },
      { label: "추세 기준선", value: 1314, tone: "neutral" },
      { label: "단기 저항", value: 1368, tone: "negative" },
    ],
    rulePresets: [
      { label: "실적 전 20일 고점 유지", description: "리더십 체크", enabled: true },
      { label: "가이던스 상향 확인", description: "실적 확장성 검증", enabled: true },
      { label: "1288 이탈", description: "추세 훼손 경계", enabled: false },
    ],
    scoreBreakdown: [
      { label: "실적 가시성", score: 88, summary: "통신 + AI 동시 노출" },
      { label: "수급 지속성", score: 83, summary: "변동성은 낮지만 꾸준한 선호" },
      { label: "밸류 부담", score: 67, summary: "대형주 내 상대적으로 무난" },
    ],
    flows: [
      { label: "기관 수급", value: "+7.6억 달러", delta: "저점 매수 우위", tone: "positive" },
      { label: "개인 수급", value: "-1.2억 달러", delta: "중립", tone: "neutral" },
      { label: "해외 수급", value: "+2.4억 달러", delta: "반도체 바스켓 편입", tone: "positive" },
    ],
    shortOptionMetrics: [
      { label: "콜/풋 비율", value: "1.22", detail: "완만한 상단 선호", tone: "positive" },
      { label: "공매도 비중", value: "0.8%", detail: "낮음", tone: "neutral" },
      { label: "암묵 변동성", value: "31%", detail: "실적 전 평균 수준", tone: "neutral" },
    ],
    issues: [
      {
        title: "네트워크 수요 상향",
        source: "브로커 리포트",
        summary: "AI 스위치 업사이클이 이어질 가능성",
        tone: "positive",
      },
    ],
    relatedSymbols: ["NVDA", "VRT", "MSFT"],
  },
  VRT: {
    symbol: "VRT",
    name: "Vertiv",
    exchange: "NYSE",
    price: 101.12,
    changePercent: 2.82,
    marketCap: "39B",
    thesis: "전력 병목이 구조적 테마로 전환되며 AI 인프라 2차 수혜가 부각.",
    chartPoints: scaleChart(baseChart, 0.11),
    indicatorGuides: [
      { label: "지지 구간", value: 96, tone: "positive" },
      { label: "추세 기준선", value: 98.5, tone: "neutral" },
      { label: "과열 경계", value: 105, tone: "negative" },
    ],
    rulePresets: [
      { label: "수주 코멘트 상향", description: "구조적 수요 확인", enabled: true },
      { label: "거래량 배수 1.4 이상", description: "추세 확인", enabled: true },
      { label: "96 이탈", description: "리스크 확대", enabled: false },
    ],
    scoreBreakdown: [
      { label: "실적 가시성", score: 81, summary: "장기 수주 잔고가 강점" },
      { label: "수급 지속성", score: 85, summary: "모멘텀 자금 유입이 강함" },
      { label: "밸류 부담", score: 63, summary: "단기 과열은 관리 필요" },
    ],
    flows: [
      { label: "기관 수급", value: "+2.1억 달러", delta: "순유입 확대", tone: "positive" },
      { label: "개인 수급", value: "-0.4억 달러", delta: "차익 실현", tone: "neutral" },
      { label: "해외 수급", value: "+0.9억 달러", delta: "AI 전력 테마 관심", tone: "positive" },
    ],
    shortOptionMetrics: [
      { label: "콜/풋 비율", value: "1.33", detail: "모멘텀 베팅 우세", tone: "positive" },
      { label: "공매도 비중", value: "3.6%", detail: "변동성 확대 가능", tone: "negative" },
      { label: "암묵 변동성", value: "47%", detail: "테마 과열 반영", tone: "negative" },
    ],
    issues: [
      {
        title: "데이터센터 전력 수주",
        source: "섹터 메모",
        summary: "공급 병목이 길어질수록 가격 협상력이 유지될 가능성",
        tone: "positive",
      },
    ],
    relatedSymbols: ["NVDA", "AVGO", "SMCI"],
  },
  CRWD: {
    symbol: "CRWD",
    name: "CrowdStrike",
    exchange: "NASDAQ",
    price: 389.41,
    changePercent: 1.55,
    marketCap: "96B",
    thesis: "방어적 성장과 플랫폼 업셀 모멘텀을 동시에 가진 보안 리더.",
    chartPoints: scaleChart(baseChart, 0.42),
    indicatorGuides: [
      { label: "지지 구간", value: 374, tone: "positive" },
      { label: "추세 기준선", value: 382, tone: "neutral" },
      { label: "단기 저항", value: 395, tone: "negative" },
    ],
    rulePresets: [
      { label: "업셀 계약 뉴스", description: "방어적 성장 확인", enabled: true },
      { label: "RS 80 이상", description: "리더십 체크", enabled: true },
      { label: "374 이탈", description: "조건 약화", enabled: false },
    ],
    scoreBreakdown: [
      { label: "실적 가시성", score: 82, summary: "계약 갱신 흐름이 안정적" },
      { label: "수급 지속성", score: 80, summary: "방어적 성장 선호 수혜" },
      { label: "밸류 부담", score: 65, summary: "금리 재상승 시 압박" },
    ],
    flows: [
      { label: "기관 수급", value: "+1.8억 달러", delta: "방어적 성장 선호", tone: "positive" },
      { label: "개인 수급", value: "+0.2억 달러", delta: "단기 추격 유입", tone: "neutral" },
      { label: "해외 수급", value: "+0.4억 달러", delta: "보안 섹터 관심", tone: "positive" },
    ],
    shortOptionMetrics: [
      { label: "콜/풋 비율", value: "1.17", detail: "중립 이상", tone: "neutral" },
      { label: "공매도 비중", value: "2.1%", detail: "과도하지 않음", tone: "neutral" },
      { label: "암묵 변동성", value: "29%", detail: "방어적 수준", tone: "positive" },
    ],
    issues: [
      {
        title: "플랫폼 번들 확장",
        source: "기업 메모",
        summary: "고객당 매출 증가가 확인되는 구간",
        tone: "positive",
      },
    ],
    relatedSymbols: ["PANW", "MSFT", "NVDA"],
  },
  MSFT: {
    symbol: "MSFT",
    name: "Microsoft",
    exchange: "NASDAQ",
    price: 468.6,
    changePercent: 0.52,
    marketCap: "3.41T",
    thesis: "클라우드와 AI 수요가 견조하지만 밸류 부담은 이미 상당 부분 반영.",
    chartPoints: scaleChart(baseChart, 0.51),
    indicatorGuides: [
      { label: "지지 구간", value: 456, tone: "positive" },
      { label: "추세 기준선", value: 462, tone: "neutral" },
      { label: "단기 저항", value: 472, tone: "negative" },
    ],
    rulePresets: [
      { label: "Azure 사용량 상향", description: "핵심 체크 포인트", enabled: true },
      { label: "실적 전 박스권 유지", description: "과열 방지", enabled: true },
      { label: "456 이탈", description: "리스크 확대", enabled: false },
    ],
    scoreBreakdown: [
      { label: "실적 가시성", score: 85, summary: "클라우드 + AI 조합이 견고" },
      { label: "수급 지속성", score: 74, summary: "대형주 안정 선호" },
      { label: "밸류 부담", score: 58, summary: "금리 민감도 남아 있음" },
    ],
    flows: [
      { label: "기관 수급", value: "+3.2억 달러", delta: "대형주 선호", tone: "positive" },
      { label: "개인 수급", value: "-0.6억 달러", delta: "차익 실현", tone: "neutral" },
      { label: "해외 수급", value: "+0.7억 달러", delta: "클라우드 선호", tone: "positive" },
    ],
    shortOptionMetrics: [
      { label: "콜/풋 비율", value: "1.05", detail: "중립", tone: "neutral" },
      { label: "공매도 비중", value: "0.6%", detail: "낮음", tone: "positive" },
      { label: "암묵 변동성", value: "24%", detail: "대형주 평균 수준", tone: "positive" },
    ],
    issues: [
      {
        title: "클라우드 사용량 체크",
        source: "채널 체크",
        summary: "AI 워크로드 확장이 Azure 매출로 얼마나 전환되는지 확인 필요",
        tone: "neutral",
      },
    ],
    relatedSymbols: ["NVDA", "CRWD", "AVGO"],
  },
};

export function buildStockFixture(symbol: string) {
  const fixture = stockFixtures[symbol.toUpperCase()];

  if (fixture) {
    return fixture;
  }

  return {
    ...stockFixtures.NVDA,
    symbol: symbol.toUpperCase(),
    name: `${symbol.toUpperCase()} Sample`,
    thesis:
      "개발용 fixture 에 없는 심볼이므로 기본 종목 분석 템플릿을 표시한다. 실제 연동 시 서버 상태로 교체하면 된다.",
  };
}
