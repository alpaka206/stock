import { findInstrument } from "@/dev/fixtures/instruments";
import type {
  ChartGuide,
  ChartOverlay,
  PatternCard,
  PricePoint,
  StockFixture,
  TechnicalMetric,
} from "@/lib/research/types";

const basePriceSeries: PricePoint[] = [
  { date: "2026-03-12", label: "03/12", close: 842, volume: 44 },
  { date: "2026-03-19", label: "03/19", close: 851, volume: 39 },
  { date: "2026-03-26", label: "03/26", close: 865, volume: 48 },
  { date: "2026-04-02", label: "04/02", close: 858, volume: 41 },
  { date: "2026-04-09", label: "04/09", close: 876, volume: 54 },
  { date: "2026-04-16", label: "04/16", close: 889, volume: 58 },
  { date: "2026-04-23", label: "04/23", close: 901, volume: 63 },
  { date: "2026-04-30", label: "04/30", close: 917, volume: 60 },
  { date: "2026-05-14", label: "05/14", close: 923, volume: 57 },
];

function scaleSeries(points: PricePoint[], multiplier: number) {
  return points.map((point) => ({
    ...point,
    close: Number((point.close * multiplier).toFixed(2)),
    volume: Number((point.volume * Math.max(0.6, Math.min(multiplier, 1.8))).toFixed(0)),
  }));
}

function buildMovingAverage(points: PricePoint[], window: number): ChartOverlay {
  return {
    id: `ma${window}`,
    label: `${window}일선`,
    tone: window <= 10 ? "positive" : "neutral",
    enabled: true,
    points: points.flatMap((point, index) => {
      const windowPoints = points.slice(Math.max(0, index - window + 1), index + 1);
      if (windowPoints.length < Math.min(window, points.length)) {
        return [];
      }

      return [
        {
          date: point.date ?? "",
          label: point.label,
          value: Number(
            (
              windowPoints.reduce((total, item) => total + item.close, 0) /
              windowPoints.length
            ).toFixed(2)
          ),
        },
      ];
    }),
  };
}

function buildFixtureChartOverlays(points: PricePoint[]): ChartOverlay[] {
  return [5, 20].map((window) => buildMovingAverage(points, window));
}

function buildFixtureTechnicalMetrics(points: PricePoint[]): TechnicalMetric[] {
  const latest = points.at(-1);
  const previous = points.at(-2);
  const closes = points.map((point) => point.close);
  const support = Math.min(...closes.slice(-6));
  const resistance = Math.max(...closes.slice(-6));
  const volumeAverage =
    points.slice(-6).reduce((total, point) => total + point.volume, 0) /
    Math.max(points.slice(-6).length, 1);
  const volumeRatio = latest ? latest.volume / volumeAverage : 0;

  return [
    {
      id: "ma-alignment",
      label: "추세",
      value: latest && previous && latest.close >= previous.close ? "상승 우위" : "중립",
      detail: "단기 가격이 이전 구간보다 높게 유지되는지 확인합니다.",
      tone: latest && previous && latest.close >= previous.close ? "positive" : "neutral",
    },
    {
      id: "volume-ratio",
      label: "거래량",
      value: `${volumeRatio.toFixed(2)}x`,
      detail: "최근 거래량이 평균보다 얼마나 강한지 비교합니다.",
      tone: volumeRatio >= 1.2 ? "positive" : "neutral",
    },
    {
      id: "support-distance",
      label: "지지선 거리",
      value: latest ? `${(((latest.close - support) / support) * 100).toFixed(2)}%` : "-",
      detail: `최근 지지선 ${support.toFixed(2)} 대비 현재 위치입니다.`,
      tone: "positive",
    },
    {
      id: "resistance-distance",
      label: "저항선 거리",
      value: latest
        ? `${(((latest.close - resistance) / resistance) * 100).toFixed(2)}%`
        : "-",
      detail: `최근 저항선 ${resistance.toFixed(2)} 대비 현재 위치입니다.`,
      tone: latest && latest.close >= resistance ? "positive" : "neutral",
    },
  ];
}

function buildFixturePatternCards(points: PricePoint[]): PatternCard[] {
  const closes = points.map((point) => point.close);
  const latest = closes.at(-1) ?? 0;
  const low = Math.min(...closes);
  const high = Math.max(...closes);
  const range = latest > 0 ? (high - low) / latest : 0;

  return [
    {
      id: "flat-base",
      label: "박스권 돌파",
      similarity: Number(Math.max(0.45, Math.min(0.86, 0.82 - range)).toFixed(2)),
      stage: latest >= high ? "상단 돌파 시도" : "박스 상단 확인",
      invalidation: `${low.toFixed(2)} 이탈`,
      summary: "좁아진 가격 범위에서 거래량이 붙는지 확인합니다.",
      tone: range <= 0.12 ? "positive" : "neutral",
    },
    {
      id: "ma-trend",
      label: "이동평균 추세",
      similarity: 0.74,
      stage: "추세 유지",
      invalidation: "20일선 이탈",
      summary: "현재가가 단기 평균 위에서 유지되는지 확인합니다.",
      tone: "positive",
    },
  ];
}

function defaultGuides(points: PricePoint[]): ChartGuide[] {
  const closes = points.map((point) => point.close);
  const support = Math.min(...closes.slice(-6));
  const resistance = Math.max(...closes.slice(-6));
  const latest = closes.at(-1) ?? resistance;

  return [
    {
      id: "support",
      label: "지지선",
      value: support,
      tone: "positive",
      description: "최근 되돌림에서 먼저 확인할 가격대입니다.",
      enabled: true,
    },
    {
      id: "trend-base",
      label: "추세 기준",
      value: latest * 0.98,
      tone: "neutral",
      description: "단기 추세가 유지되는지 보는 기준입니다.",
      enabled: true,
    },
    {
      id: "resistance",
      label: "저항선",
      value: resistance * 1.02,
      tone: "negative",
      description: "단기 과열을 확인할 가격대입니다.",
      enabled: true,
    },
  ];
}

function createStockFixture(
  symbol: string,
  overrides: Omit<
    StockFixture,
    "instrument" | "dataSource" | "chartOverlays" | "technicalMetrics" | "patternCards"
  > & {
    instrument: Partial<StockFixture["instrument"]>;
    chartOverlays?: ChartOverlay[];
    technicalMetrics?: TechnicalMetric[];
    patternCards?: PatternCard[];
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
    chartOverlays: overrides.chartOverlays ?? buildFixtureChartOverlays(overrides.priceSeries),
    technicalMetrics:
      overrides.technicalMetrics ?? buildFixtureTechnicalMetrics(overrides.priceSeries),
    patternCards: overrides.patternCards ?? buildFixturePatternCards(overrides.priceSeries),
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
      label: "목데이터",
      description: "API 키 또는 백엔드 연결이 없어 실제 데이터 대신 표시한 종목 데이터입니다. (목데이터)",
    },
  };
}

const defaultRules = [
  {
    id: "support-hold",
    label: "지지선 유지",
    description: "최근 지지선 위에서 가격이 유지되는지 확인합니다.",
    enabledByDefault: true,
    tone: "positive" as const,
    guideIds: ["support"],
  },
  {
    id: "ma-trend",
    label: "이동평균 추세",
    description: "단기 이동평균과 20일선 흐름을 함께 봅니다.",
    enabledByDefault: true,
    tone: "neutral" as const,
    guideIds: ["ma5", "ma20", "trend-base"],
  },
  {
    id: "volume-spike",
    label: "거래량 확인",
    description: "가격 상승에 거래량이 동반되는지 봅니다.",
    enabledByDefault: true,
    tone: "positive" as const,
    guideIds: ["volume"],
  },
  {
    id: "event-window",
    label: "이벤트 구간",
    description: "실적, 공시, 발표 전후의 변동성을 함께 표시합니다.",
    enabledByDefault: true,
    tone: "neutral" as const,
    controlsEventMarkers: true,
  },
];

export const stockFixtures: Record<string, StockFixture> = {
  NVDA: createStockFixture("NVDA", {
    instrument: {
      marketCap: "2.28T",
      sector: "반도체",
    },
    price: 923.42,
    changePercent: 2.16,
    thesis:
      "AI 서버 투자 흐름의 핵심 종목입니다. 다만 이벤트 기대가 높아 발표 직후 변동성 관리는 필요합니다.",
    priceSeries: basePriceSeries,
    eventMarkers: [
      {
        id: "nvda-earnings",
        label: "실적",
        tone: "positive",
        date: "2026-04-16",
        title: "실적과 가이던스 상향",
        detail: "데이터센터 매출이 예상보다 강했고 다음 분기 가이던스도 상향됐습니다.",
      },
      {
        id: "nvda-gtc",
        label: "발표",
        tone: "neutral",
        date: "2026-04-30",
        title: "GTC 발표",
        detail: "신제품 로드맵 기대가 유지되지만 단기 과열도 함께 확인해야 합니다.",
      },
    ],
    indicatorGuides: defaultGuides(basePriceSeries),
    rulePresetDefinitions: defaultRules,
    scoreSummary: {
      total: 86,
      confidence: {
        score: 0.81,
        label: "high",
        rationale: "가격, 거래량, 이벤트가 같은 방향으로 움직여 판단 근거가 비교적 많습니다.",
      },
      breakdown: [
        { label: "차트 추세", score: 90, summary: "상승 추세가 유지되고 최근 저항선 돌파를 시도합니다." },
        { label: "거래와 수급", score: 84, summary: "거래량이 평균보다 높은 구간에서 가격이 유지됩니다." },
        { label: "이벤트", score: 92, summary: "실적과 제품 발표가 모두 긍정적인 방향입니다." },
        { label: "리스크", score: 77, summary: "이벤트 후 기대가 되돌려질 가능성은 남아 있습니다." },
      ],
    },
    flowMetrics: [
      {
        label: "기관 수급",
        value: "확인 필요",
        detail: "실서비스에서는 거래소와 데이터 제공사 수급 API로 대체합니다.",
        tone: "neutral",
      },
    ],
    flowUnavailable: {
      label: "실시간 수급 연결 전",
      reason: "무료 범위에서 검증 가능한 수급 데이터가 아직 연결되지 않았습니다.",
      expectedSource: "거래소 또는 데이터 제공사 수급 API",
    },
    optionsShortMetrics: [
      {
        label: "옵션 프리미엄",
        value: "높음",
        detail: "이벤트 전후 변동성 확대 가능성을 확인해야 합니다.",
        tone: "negative",
      },
    ],
    optionsUnavailable: {
      label: "공매도 상세 연결 전",
      reason: "공매도와 옵션 상세 비율은 별도 provider 연결 후 표시합니다.",
      expectedSource: "옵션/공매도 데이터 provider",
    },
    issues: [
      {
        title: "AI 서버 투자 지속",
        source: "시장 브리프 (목데이터)",
        summary: "대형 클라우드 기업의 AI 투자 확대가 실적 기대를 지지합니다.",
        tone: "positive",
        category: "섹터",
        href: "/radar",
      },
      {
        title: "이벤트 기대 과열",
        source: "리스크 메모 (목데이터)",
        summary: "발표 직전 기대가 높아진 만큼 작은 실망에도 변동성이 커질 수 있습니다.",
        tone: "negative",
        category: "리스크",
        href: "/history?symbol=NVDA",
      },
    ],
    relatedSymbols: ["AVGO", "000660.KS", "MSFT"],
  }),
  "000660.KS": createStockFixture("000660.KS", {
    instrument: {
      marketCap: "139T KRW",
      exchange: "KRX",
      sector: "반도체",
    },
    price: 191500,
    changePercent: 1.94,
    thesis:
      "HBM 수요와 외국인 수급이 동시에 우호적입니다. 다만 환율과 메모리 가격 지표를 함께 확인해야 합니다.",
    priceSeries: scaleSeries(basePriceSeries, 207.5),
    eventMarkers: [
      {
        id: "hynix-hbm",
        label: "HBM",
        tone: "positive",
        date: "2026-04-23",
        title: "HBM 공급 코멘트",
        detail: "고부가 메모리 수요가 실적 기대를 지지합니다.",
      },
    ],
    indicatorGuides: defaultGuides(scaleSeries(basePriceSeries, 207.5)),
    rulePresetDefinitions: defaultRules,
    scoreSummary: {
      total: 88,
      confidence: {
        score: 0.74,
        label: "medium",
        rationale: "섹터 모멘텀은 강하지만 국내 수급과 환율 확인이 필요합니다.",
      },
      breakdown: [
        { label: "차트 추세", score: 86, summary: "최근 고점 돌파 흐름이 유지됩니다." },
        { label: "거래와 수급", score: 88, summary: "거래량과 외국인 관심이 함께 증가하는 구간입니다." },
        { label: "이벤트", score: 90, summary: "HBM 공급 코멘트가 핵심 촉매입니다." },
        { label: "리스크", score: 74, summary: "환율과 메모리 가격 변동성은 계속 확인해야 합니다." },
      ],
    },
    flowMetrics: [],
    flowUnavailable: {
      label: "투자자별 수급 연결 전",
      reason: "국내 투자자별 순매수 데이터 API 연결 후 표시합니다.",
      expectedSource: "KRX 또는 증권 데이터 provider",
    },
    optionsShortMetrics: [],
    optionsUnavailable: {
      label: "공매도 상세 연결 전",
      reason: "공매도 잔고와 대차 데이터는 별도 provider 연결이 필요합니다.",
      expectedSource: "KRX 공매도/대차 데이터",
    },
    issues: [
      {
        title: "HBM 공급 가시성",
        source: "섹터 메모 (목데이터)",
        summary: "고부가 메모리 수요가 실적 기대를 끌어올리는 구간입니다.",
        tone: "positive",
        category: "섹터",
        href: "/radar?sector=반도체",
      },
    ],
    relatedSymbols: ["005930.KS", "NVDA", "AVGO"],
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
      name: findInstrument(normalizedSymbol)?.name ?? normalizedSymbol,
      marketCap: "미제공",
      sector: findInstrument(normalizedSymbol)?.sector ?? "기타",
    },
    price: stockFixtures.NVDA.price,
    changePercent: stockFixtures.NVDA.changePercent,
    thesis:
      "아직 전용 예시 데이터가 없는 종목입니다. 실제 API가 연결되면 가격, 뉴스, 공시, 차트가 해당 종목 기준으로 대체됩니다.",
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
