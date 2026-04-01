import { findInstrument } from "@/dev/fixtures/instruments";
import type { PricePoint, StockFixture } from "@/lib/research/types";

const basePriceSeries: PricePoint[] = [
  { date: "2026-02-12", label: "02/12", close: 842, volume: 44 },
  { date: "2026-02-19", label: "02/19", close: 851, volume: 39 },
  { date: "2026-02-26", label: "02/26", close: 865, volume: 48 },
  { date: "2026-03-05", label: "03/05", close: 858, volume: 41 },
  { date: "2026-03-10", label: "03/10", close: 876, volume: 54 },
  { date: "2026-03-13", label: "03/13", close: 889, volume: 58 },
  { date: "2026-03-17", label: "03/17", close: 901, volume: 63 },
  { date: "2026-03-19", label: "03/19", close: 917, volume: 60 },
  { date: "2026-03-21", label: "03/21", close: 923, volume: 57 },
];

function scaleSeries(points: PricePoint[], multiplier: number) {
  return points.map((point) => ({
    ...point,
    close: Number((point.close * multiplier).toFixed(2)),
  }));
}

function createStockFixture(
  symbol: string,
  overrides: Omit<StockFixture, "instrument" | "dataSource"> & {
    instrument: Partial<StockFixture["instrument"]>;
  }
): StockFixture {
  const catalog = findInstrument(symbol);

  return {
    instrument: {
      symbol,
      name: catalog?.name ?? symbol,
      exchange: catalog?.exchange ?? "NASDAQ",
      securityCode: catalog?.securityCode ?? `${symbol}-000`,
      sector: catalog?.sector ?? "기타",
      marketCap: overrides.instrument.marketCap ?? "미제공",
      ...overrides.instrument,
    },
    price: overrides.price,
    changePercent: overrides.changePercent,
    thesis: overrides.thesis,
    priceSeries: overrides.priceSeries,
    eventMarkers: overrides.eventMarkers,
    indicatorGuides: overrides.indicatorGuides,
    rulePresetDefinitions: overrides.rulePresetDefinitions,
    scoreSummary: overrides.scoreSummary,
    flowMetrics: overrides.flowMetrics,
    flowUnavailable: overrides.flowUnavailable,
    optionsShortMetrics: overrides.optionsShortMetrics,
    optionsUnavailable: overrides.optionsUnavailable,
    issues: overrides.issues,
    relatedSymbols: overrides.relatedSymbols,
    dataSource: {
      mode: "fixture",
      label: "샘플 데이터",
      description: "API가 연결되지 않은 개발 환경 기본 종목 fixture입니다.",
    },
  };
}

export const stockFixtures: Record<string, StockFixture> = {
  NVDA: createStockFixture("NVDA", {
    instrument: {
      marketCap: "2.28T",
      sector: "반도체",
    },
    price: 923.42,
    changePercent: 2.16,
    thesis:
      "AI 서버 CAPEX 확대가 유지되는 동안 핵심 리더로 남아 있지만, 이벤트 직후에는 변동성이 커질 수 있어 가격 레벨과 거래량을 함께 확인해야 한다.",
    priceSeries: basePriceSeries,
    eventMarkers: [
      {
        id: "nvda-earnings",
        label: "실적",
        tone: "positive",
        date: "2026-03-13",
        title: "실적과 가이던스 상향",
        detail: "데이터센터 매출이 예상보다 강했고 다음 분기 가이던스도 상향됐다.",
      },
      {
        id: "nvda-gtc",
        label: "GTC",
        tone: "neutral",
        date: "2026-03-19",
        title: "GTC 발표",
        detail: "신규 플랫폼 발표 이후 기대가 유지되지만 단기 과열 해소 구간 여부를 확인해야 한다.",
      },
    ],
    indicatorGuides: [
      {
        id: "support",
        label: "지지 구간",
        value: 889,
        tone: "positive",
        description: "최근 돌파 구간이 첫 번째 방어선 역할을 하는지 본다.",
        enabled: true,
      },
      {
        id: "trend-base",
        label: "추세 기준선",
        value: 901,
        tone: "neutral",
        description: "20일 평균 회복 여부를 추세 유지 판단선으로 사용한다.",
        enabled: true,
      },
      {
        id: "resistance",
        label: "저항 구간",
        value: 938,
        tone: "negative",
        description: "단기 과열 경계 구간이다.",
        enabled: true,
      },
      {
        id: "relative-strength",
        label: "상대강도 기준",
        value: 88,
        tone: "positive",
        description: "리더 유지 여부를 확인하는 상대강도 기준선이다.",
        enabled: true,
      },
      {
        id: "volume-spike",
        label: "거래량 배수",
        value: 1.4,
        tone: "positive",
        description: "돌파 신뢰도를 판단하는 거래량 기준이다.",
        enabled: true,
      },
      {
        id: "volatility",
        label: "변동성 경계",
        value: 4.2,
        tone: "negative",
        description: "이벤트 이후 일중 흔들림이 커질 수 있는 수준이다.",
        enabled: false,
      },
    ],
    rulePresetDefinitions: [
      {
        id: "support-hold",
        label: "지지선 유지",
        description: "889 위에서 지지가 유지되는지 확인한다.",
        enabledByDefault: true,
        tone: "positive",
      },
      {
        id: "trend-base",
        label: "추세선 회복",
        description: "20일 추세 기준선 위에서 종가가 유지되는지 본다.",
        enabledByDefault: true,
        tone: "neutral",
      },
      {
        id: "volume-spike",
        label: "거래량 배수 1.4x",
        description: "기관 수급이 붙는 돌파인지 거래량으로 확인한다.",
        enabledByDefault: true,
        tone: "positive",
      },
      {
        id: "relative-strength",
        label: "상대강도 80 이상",
        description: "리더십 유지 여부를 점검한다.",
        enabledByDefault: true,
        tone: "positive",
      },
      {
        id: "volatility-guard",
        label: "변동성 경계",
        description: "이벤트 직후 변동성 확대 여부를 경고한다.",
        enabledByDefault: false,
        tone: "negative",
      },
      {
        id: "event-window",
        label: "이벤트 창 관리",
        description: "실적·행사 직전후 포지션 과열을 막는다.",
        enabledByDefault: true,
        tone: "neutral",
      },
    ],
    scoreSummary: {
      total: 86,
      confidence: {
        score: 0.81,
        label: "high",
        rationale: "가격, 거래량, 뉴스 이벤트가 모두 같은 방향을 가리켜 판단 근거가 비교적 많다.",
      },
      breakdown: [
        {
          label: "기술 추세",
          score: 90,
          summary: "상승 추세가 유지되고 최근 돌파 구간도 아직 훼손되지 않았다.",
        },
        {
          label: "수급/유동성",
          score: 84,
          summary: "거래량이 붙는 구간이 반복돼 추세의 질이 나쁘지 않다.",
        },
        {
          label: "촉매/이슈",
          score: 92,
          summary: "실적과 제품 이벤트가 동시에 서포트하는 구조다.",
        },
        {
          label: "리스크 관리",
          score: 77,
          summary: "이벤트 이후 변동성 확대 가능성 때문에 과열 경계가 필요하다.",
        },
      ],
    },
    flowMetrics: [
      {
        label: "기관 수급 메모",
        value: "확인 필요",
        detail: "실제 기관·개인·외국인 수급 API가 연결되면 이 영역이 대체된다.",
        tone: "neutral",
      },
    ],
    flowUnavailable: {
      label: "수급 데이터 준비 중",
      reason: "무료 범위에서 기관/개인/외국인 수급 API를 아직 연결하지 않았다.",
      expectedSource: "국내 수급 provider",
    },
    optionsShortMetrics: [
      {
        label: "옵션/공매도 메모",
        value: "준비 중",
        detail: "실제 공매도·옵션 비율은 아직 연결되지 않았다.",
        tone: "neutral",
      },
    ],
    optionsUnavailable: {
      label: "공매도/옵션 데이터 준비 중",
      reason: "무료 데이터 범위에서 실시간 옵션·공매도 비율을 제공하지 않는다.",
      expectedSource: "옵션/공매도 provider",
    },
    issues: [
      {
        title: "패키지 공급 병목 완화",
        source: "공급망 메모",
        summary: "하반기 출하량 상향 가능성을 다시 점검하는 구간이다.",
        tone: "positive",
        category: "종목",
        href: "/history?symbol=NVDA",
      },
      {
        title: "전력 인프라 병목 지속",
        source: "섹터 메모",
        summary: "AI 증설 속도는 빠르지만 전력·서버 랙 병목이 동반된다.",
        tone: "neutral",
        category: "섹터",
        href: "/radar?sector=전력 인프라",
      },
      {
        title: "이벤트 기대 과열 구간",
        source: "리스크 메모",
        summary: "행사 직전 기대감이 높아 단기 흔들림이 커질 수 있다.",
        tone: "negative",
        category: "시황",
        href: "/history?symbol=NVDA",
      },
    ],
    relatedSymbols: ["AVGO", "AMD", "VRT"],
  }),
  AVGO: createStockFixture("AVGO", {
    instrument: {
      marketCap: "626B",
      sector: "반도체",
    },
    price: 1345.88,
    changePercent: 1.34,
    thesis: "커스텀 AI 칩과 네트워크가 동시에 살아 있는 종목으로, 실적 확인 뒤 추세 복귀를 보는 구간이다.",
    priceSeries: scaleSeries(basePriceSeries, 1.46),
    eventMarkers: [
      {
        id: "avgo-earnings",
        label: "실적",
        tone: "positive",
        date: "2026-03-17",
        title: "AI 매출 가이던스 상향",
        detail: "네트워크와 커스텀 칩 수요가 예상보다 강했다.",
      },
    ],
    indicatorGuides: [
      {
        id: "support",
        label: "지지 구간",
        value: 1288,
        tone: "positive",
        description: "최근 눌림 시 방어선이다.",
        enabled: true,
      },
      {
        id: "trend-base",
        label: "추세 기준선",
        value: 1314,
        tone: "neutral",
        description: "추세 재가속 여부를 보는 기준선이다.",
        enabled: true,
      },
      {
        id: "resistance",
        label: "저항 구간",
        value: 1368,
        tone: "negative",
        description: "고점 매물 부담 구간이다.",
        enabled: true,
      },
      {
        id: "volume",
        label: "거래량 배수",
        value: 1.2,
        tone: "positive",
        description: "실적 이후 거래량 유지 여부를 확인한다.",
        enabled: true,
      },
      {
        id: "relative-strength",
        label: "상대강도",
        value: 82,
        tone: "positive",
        description: "반도체 내 리더 그룹 유지 여부를 점검한다.",
        enabled: true,
      },
      {
        id: "volatility",
        label: "변동성",
        value: 3.4,
        tone: "neutral",
        description: "과열은 아니지만 흔들림이 커질 수 있다.",
        enabled: false,
      },
    ],
    rulePresetDefinitions: [
      {
        id: "earnings-followthrough",
        label: "실적 후 추세 확인",
        description: "실적 발표 후 거래량이 이어지는지 본다.",
        enabledByDefault: true,
      },
      {
        id: "trend-base",
        label: "추세선 유지",
        description: "1314 위에서 종가가 유지되는지 확인한다.",
        enabledByDefault: true,
      },
      {
        id: "support-hold",
        label: "1288 지지선",
        description: "눌림 이후 구조 훼손 여부를 체크한다.",
        enabledByDefault: true,
      },
      {
        id: "rs80",
        label: "상대강도 80",
        description: "리더십 유지 기준으로 본다.",
        enabledByDefault: true,
      },
      {
        id: "volume-1-2",
        label: "거래량 배수 1.2x",
        description: "추세 신뢰도를 판단한다.",
        enabledByDefault: true,
      },
      {
        id: "macro-risk",
        label: "금리 민감도",
        description: "금리 반등 시 대형주 밸류에이션 압박을 경고한다.",
        enabledByDefault: false,
      },
    ],
    scoreSummary: {
      total: 81,
      confidence: {
        score: 0.74,
        label: "medium",
        rationale: "기술적 구조는 양호하지만 macro 민감도와 밸류에이션 부담이 함께 존재한다.",
      },
      breakdown: [
        { label: "기술 추세", score: 84, summary: "눌림 이후 추세 재가속 가능성이 남아 있다." },
        { label: "수급/유동성", score: 78, summary: "거래량이 받쳐주지만 과도한 몰림은 아니다." },
        { label: "촉매/이슈", score: 86, summary: "실적과 AI 수요가 동시에 지지한다." },
        { label: "리스크 관리", score: 74, summary: "금리와 대형주 밸류 부담을 체크해야 한다." },
      ],
    },
    flowMetrics: [],
    flowUnavailable: {
      label: "수급 데이터 준비 중",
      reason: "기관/개인/외국인 수급 API 미연결 상태다.",
      expectedSource: "flow provider",
    },
    optionsShortMetrics: [],
    optionsUnavailable: {
      label: "옵션/공매도 데이터 준비 중",
      reason: "실제 비율 계산용 데이터 소스가 아직 없다.",
      expectedSource: "options-short provider",
    },
    issues: [
      {
        title: "커스텀 칩 수요 지속",
        source: "브로커 요약",
        summary: "AI 데이터센터 고객사 확장으로 가시성이 유지된다.",
        tone: "positive",
      },
    ],
    relatedSymbols: ["NVDA", "VRT", "MSFT"],
  }),
  VRT: createStockFixture("VRT", {
    instrument: {
      marketCap: "39B",
      sector: "전력 인프라",
      exchange: "NYSE",
    },
    price: 101.12,
    changePercent: 2.82,
    thesis: "전력 병목이 구조적 이슈로 전환되며 AI 인프라 2차 수혜가 붙는 종목이다.",
    priceSeries: scaleSeries(basePriceSeries, 0.11),
    eventMarkers: [
      {
        id: "vrt-capex",
        label: "수주",
        tone: "positive",
        date: "2026-03-17",
        title: "전력 설비 수주 메모",
        detail: "데이터센터 전력 증설 계획이 재차 확인됐다.",
      },
    ],
    indicatorGuides: [
      {
        id: "support",
        label: "지지 구간",
        value: 96,
        tone: "positive",
        enabled: true,
      },
      {
        id: "trend-base",
        label: "추세 기준선",
        value: 98.5,
        tone: "neutral",
        enabled: true,
      },
      {
        id: "resistance",
        label: "저항 구간",
        value: 105,
        tone: "negative",
        enabled: true,
      },
      {
        id: "volume",
        label: "거래량 배수",
        value: 1.5,
        tone: "positive",
        enabled: true,
      },
      {
        id: "relative-strength",
        label: "상대강도",
        value: 86,
        tone: "positive",
        enabled: true,
      },
      {
        id: "volatility",
        label: "변동성",
        value: 5.1,
        tone: "negative",
        enabled: false,
      },
    ],
    rulePresetDefinitions: [
      {
        id: "power-trend",
        label: "전력 테마 추세",
        description: "전력 병목 내러티브가 유지되는지 점검한다.",
        enabledByDefault: true,
      },
      {
        id: "support-hold",
        label: "96 지지선",
        description: "단기 눌림 이후 구조 훼손 여부를 본다.",
        enabledByDefault: true,
      },
      {
        id: "volume-1-4",
        label: "거래량 배수 1.4x",
        description: "테마 확산에 거래량이 따라오는지 확인한다.",
        enabledByDefault: true,
      },
      {
        id: "rs85",
        label: "상대강도 85",
        description: "테마 리더 유지 여부를 본다.",
        enabledByDefault: true,
      },
      {
        id: "event-window",
        label: "수주 이벤트 창",
        description: "수주 기사 직전후 급등 추격을 제한한다.",
        enabledByDefault: true,
      },
      {
        id: "volatility",
        label: "변동성 경계",
        description: "테마 과열 시 흔들림 확대를 경고한다.",
        enabledByDefault: false,
      },
    ],
    scoreSummary: {
      total: 79,
      confidence: {
        score: 0.71,
        label: "medium",
        rationale: "전력 병목 논리는 명확하지만 변동성이 높아 확신도는 한 단계 낮다.",
      },
      breakdown: [
        { label: "기술 추세", score: 80, summary: "돌파 이후 눌림을 소화하는 구조다." },
        { label: "수급/유동성", score: 82, summary: "거래량이 붙는 구간이 반복된다." },
        { label: "촉매/이슈", score: 86, summary: "AI 전력 병목 수혜 논리가 명확하다." },
        { label: "리스크 관리", score: 68, summary: "과열 이후 흔들림이 큰 종목군이다." },
      ],
    },
    flowMetrics: [],
    flowUnavailable: {
      label: "수급 데이터 준비 중",
      reason: "실제 수급 source 미연결 상태다.",
    },
    optionsShortMetrics: [],
    optionsUnavailable: {
      label: "공매도/옵션 데이터 준비 중",
      reason: "실측 비율 없이 임의 수치를 만들지 않는다.",
    },
    issues: [
      {
        title: "데이터센터 전력 병목",
        source: "섹터 메모",
        summary: "전력 설비 병목이 장기 테마로 전환되는지 확인해야 한다.",
        tone: "positive",
      },
    ],
    relatedSymbols: ["NVDA", "AVGO", "SMCI"],
  }),
};

export function buildStockFixture(symbol: string) {
  const normalizedSymbol = symbol.toUpperCase();
  const fixture = stockFixtures[normalizedSymbol];

  if (fixture) {
    return fixture;
  }

  return createStockFixture(normalizedSymbol, {
    instrument: {
      name: `${normalizedSymbol} 샘플`,
      marketCap: "미제공",
      sector: "기타",
    },
    price: stockFixtures.NVDA.price,
    changePercent: stockFixtures.NVDA.changePercent,
    thesis:
      "개발용 fixture에 없는 종목이므로 기본 분석 워크스테이션 구조를 그대로 보여준다. 실제 연결 시 서버 데이터로 대체된다.",
    priceSeries: stockFixtures.NVDA.priceSeries,
    eventMarkers: stockFixtures.NVDA.eventMarkers,
    indicatorGuides: stockFixtures.NVDA.indicatorGuides,
    rulePresetDefinitions: stockFixtures.NVDA.rulePresetDefinitions,
    scoreSummary: stockFixtures.NVDA.scoreSummary,
    flowMetrics: stockFixtures.NVDA.flowMetrics,
    flowUnavailable: stockFixtures.NVDA.flowUnavailable,
    optionsShortMetrics: stockFixtures.NVDA.optionsShortMetrics,
    optionsUnavailable: stockFixtures.NVDA.optionsUnavailable,
    issues: stockFixtures.NVDA.issues,
    relatedSymbols: stockFixtures.NVDA.relatedSymbols,
  });
}
