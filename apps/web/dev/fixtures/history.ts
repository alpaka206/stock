import type { HistoryFixture } from "@/lib/research/types";

export const historyFixture: HistoryFixture = {
  symbol: "NVDA",
  range: "2025-12-01 ~ 2026-05-14",
  availableRanges: [
    { value: "1m", label: "1개월" },
    { value: "3m", label: "3개월" },
    { value: "6m", label: "6개월" },
    { value: "event", label: "이벤트 구간" },
  ],
  priceSeries: [
    { date: "2025-12-01", label: "12/01", close: 612, volume: 38 },
    { date: "2025-12-22", label: "12/22", close: 648, volume: 42 },
    { date: "2026-01-12", label: "01/12", close: 701, volume: 47 },
    { date: "2026-02-02", label: "02/02", close: 736, volume: 44 },
    { date: "2026-02-23", label: "02/23", close: 718, volume: 36 },
    { date: "2026-03-16", label: "03/16", close: 782, volume: 58 },
    { date: "2026-04-06", label: "04/06", close: 835, volume: 62 },
    { date: "2026-04-27", label: "04/27", close: 881, volume: 64 },
    { date: "2026-05-14", label: "05/14", close: 923, volume: 57 },
  ],
  eventMarkers: [
    {
      id: "history-event-1",
      label: "섹터",
      tone: "positive",
      date: "2025-12-22",
      title: "AI 서버 투자 확대",
      detail: "클라우드 기업의 AI 투자 확대 뉴스가 주도주에 자금을 모았습니다.",
    },
    {
      id: "history-event-2",
      label: "거시",
      tone: "negative",
      date: "2026-02-23",
      title: "장기 금리 반등",
      detail: "금리 반등으로 성장주 밸류에이션 부담이 커졌습니다.",
    },
    {
      id: "history-event-3",
      label: "실적",
      tone: "positive",
      date: "2026-03-16",
      title: "가이던스 상향",
      detail: "데이터센터 매출 전망이 상향되며 추세가 다시 강해졌습니다.",
    },
    {
      id: "history-event-4",
      label: "발표",
      tone: "neutral",
      date: "2026-05-14",
      title: "제품 발표 기대",
      detail: "이벤트 기대가 가격과 거래량에 먼저 반영됐습니다.",
    },
  ],
  events: [
    {
      id: "history-event-1",
      date: "2025-12-22",
      title: "AI 서버 투자 확대",
      category: "섹터",
      summary: "클라우드 기업의 AI 투자 확대가 반도체 리더 종목으로 자금을 모았습니다. (목데이터)",
      reaction: "3주 +11%",
      tone: "positive",
      source: "섹터 메모 (목데이터)",
      url: "",
    },
    {
      id: "history-event-2",
      date: "2026-02-23",
      title: "장기 금리 반등",
      category: "거시",
      summary: "성장주 밸류에이션 부담이 커지며 단기 조정이 나왔습니다. (목데이터)",
      reaction: "2주 -6%",
      tone: "negative",
      source: "거시 브리프 (목데이터)",
      url: "",
    },
    {
      id: "history-event-3",
      date: "2026-03-16",
      title: "가이던스 상향",
      category: "실적",
      summary: "실적과 다음 분기 전망이 예상보다 좋아 추세가 다시 강해졌습니다. (목데이터)",
      reaction: "4주 +13%",
      tone: "positive",
      source: "실적 발표 (목데이터)",
      url: "",
    },
    {
      id: "history-event-4",
      date: "2026-05-14",
      title: "제품 발표 기대",
      category: "이벤트",
      summary: "발표 전 기대감이 옵션 프리미엄과 거래량을 끌어올렸습니다. (목데이터)",
      reaction: "5일 +4.8%",
      tone: "neutral",
      source: "이벤트 메모 (목데이터)",
      url: "",
    },
  ],
  moveSummary:
    "상승 구간은 AI 투자 확대와 실적 상향이 겹친 결과이고, 조정 구간은 금리 반등에 따른 밸류에이션 부담이 주된 이유였습니다. (목데이터)",
  moveReasons: [
    {
      label: "상승 구간 핵심 이유",
      description: "AI 서버 투자 확대와 실적 가이던스 상향이 겹치며 자금이 리더 종목에 집중됐습니다. (목데이터)",
      tone: "positive",
      relatedDate: "2026-03-16",
    },
    {
      label: "조정 구간 핵심 이유",
      description: "장기 금리 반등으로 성장주 밸류에이션 부담이 커졌고 단기 추격 매수가 줄었습니다. (목데이터)",
      tone: "negative",
      relatedDate: "2026-02-23",
    },
    {
      label: "현재 해석",
      description: "이벤트 기대가 남아 있지만 과열 여부는 가격과 거래량을 함께 확인해야 합니다. (목데이터)",
      tone: "neutral",
      relatedDate: "2026-05-14",
    },
  ],
  overlaps: [
    {
      label: "거래량 + 상대강도",
      detail: "실적 상향 직후 거래량과 상대강도가 동시에 강해졌습니다. (목데이터)",
      tone: "positive",
      relatedDate: "2026-03-16",
    },
    {
      label: "금리 + 밸류에이션",
      detail: "금리 반등 구간에는 가격이 단기 평균 아래로 밀렸습니다. (목데이터)",
      tone: "negative",
      relatedDate: "2026-02-23",
    },
    {
      label: "이벤트 기대 + 변동성",
      detail: "발표 직전에는 거래량 증가와 단기 변동성이 함께 나타났습니다. (목데이터)",
      tone: "neutral",
      relatedDate: "2026-05-14",
    },
  ],
  dataSource: {
    mode: "fixture",
    label: "목데이터",
    description: "API 키 또는 백엔드 연결이 없어 실제 데이터 대신 표시한 히스토리 데이터입니다. (목데이터)",
  },
};

export function buildHistoryFixture(symbol = historyFixture.symbol): HistoryFixture {
  return {
    ...historyFixture,
    symbol: symbol.toUpperCase(),
  };
}
