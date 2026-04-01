import type { HistoryFixture } from "@/lib/research/types";

export const historyFixture: HistoryFixture = {
  symbol: "NVDA",
  range: "2025-10-01 ~ 2026-03-21",
  availableRanges: [
    { value: "1m", label: "1개월" },
    { value: "3m", label: "3개월" },
    { value: "6m", label: "6개월" },
    { value: "event", label: "이벤트 구간" },
  ],
  priceSeries: [
    { date: "2025-10-01", label: "10/01", close: 612, volume: 38 },
    { date: "2025-10-22", label: "10/22", close: 648, volume: 42 },
    { date: "2025-11-12", label: "11/12", close: 701, volume: 47 },
    { date: "2025-12-03", label: "12/03", close: 736, volume: 44 },
    { date: "2025-12-24", label: "12/24", close: 718, volume: 36 },
    { date: "2026-01-14", label: "01/14", close: 782, volume: 58 },
    { date: "2026-02-04", label: "02/04", close: 835, volume: 62 },
    { date: "2026-02-25", label: "02/25", close: 881, volume: 64 },
    { date: "2026-03-21", label: "03/21", close: 923, volume: 57 },
  ],
  eventMarkers: [
    {
      id: "history-event-1",
      label: "섹터",
      tone: "positive",
      date: "2025-10-22",
      title: "AI 서버 투자 확대",
      detail: "공급망 메모와 서버 증설 뉴스가 함께 나오며 테마 리더가 강화됐다.",
    },
    {
      id: "history-event-2",
      label: "매크로",
      tone: "negative",
      date: "2025-12-24",
      title: "장기 금리 급반등",
      detail: "성장주 밸류에이션 압박이 커지며 조정 구간이 나타났다.",
    },
    {
      id: "history-event-3",
      label: "실적",
      tone: "positive",
      date: "2026-01-14",
      title: "가이던스 상향",
      detail: "출하량과 마진이 동시에 상향되며 추세가 다시 강해졌다.",
    },
    {
      id: "history-event-4",
      label: "이벤트",
      tone: "neutral",
      date: "2026-03-21",
      title: "행사 기대 확산",
      detail: "이벤트 기대감이 옵션 프리미엄과 거래량을 밀어올렸다.",
    },
  ],
  events: [
    {
      id: "history-event-1",
      date: "2025-10-22",
      title: "AI 서버 투자 확대",
      category: "섹터",
      summary: "공급망 메모와 증설 뉴스가 겹치면서 리더 종목으로 자금이 모였다.",
      reaction: "3주 +11%",
      tone: "positive",
      source: "섹터 메모",
      url: "",
    },
    {
      id: "history-event-2",
      date: "2025-12-24",
      title: "장기 금리 급반등",
      category: "매크로",
      summary: "성장주 밸류 부담이 커지며 단기 조정 구간이 나타났다.",
      reaction: "2주 -6%",
      tone: "negative",
      source: "매크로 브리프",
      url: "",
    },
    {
      id: "history-event-3",
      date: "2026-01-14",
      title: "가이던스 상향",
      category: "실적",
      summary: "출하량과 마진이 예상보다 강해 추세가 다시 열렸다.",
      reaction: "4주 +13%",
      tone: "positive",
      source: "실적 발표",
      url: "",
    },
    {
      id: "history-event-4",
      date: "2026-03-21",
      title: "행사 기대 확산",
      category: "이벤트",
      summary: "행사 직전 기대감이 높아지며 옵션 프리미엄과 거래량이 동시에 뛰었다.",
      reaction: "5일 +4.8%",
      tone: "neutral",
      source: "이벤트 메모",
      url: "",
    },
  ],
  moveSummary:
    "급등 구간은 실적 상향과 AI 인프라 투자 확대가 겹친 결과였고, 급락 구간은 장기 금리 반등에 따른 밸류 부담이 주된 원인이었다.",
  moveReasons: [
    {
      label: "급등 구간 핵심 이유",
      description: "AI 서버 CAPEX 확대와 실적 가이던스 상향이 겹치며 자금이 리더 종목에 집중됐다.",
      tone: "positive",
      relatedDate: "2026-01-14",
    },
    {
      label: "조정 구간 핵심 이유",
      description: "장기 금리 급반등으로 성장주 밸류 부담이 커지면서 추격 매수 흐름이 꺾였다.",
      tone: "negative",
      relatedDate: "2025-12-24",
    },
    {
      label: "현재 해석",
      description: "이벤트 기대는 여전히 남아 있지만 과열 구간에 가까워졌는지 가격과 거래량을 함께 봐야 한다.",
      tone: "neutral",
      relatedDate: "2026-03-21",
    },
  ],
  overlaps: [
    {
      label: "거래량 + 상대강도 중첩",
      detail: "실적 상향 직후 거래량과 상대강도가 동시에 강화되며 추세 전환 신호가 겹쳤다.",
      tone: "positive",
      relatedDate: "2026-01-14",
    },
    {
      label: "금리 + 밸류 압박",
      detail: "금리 반등 구간에는 가격이 추세선 아래로 밀리며 밸류 부담 신호가 중첩됐다.",
      tone: "negative",
      relatedDate: "2025-12-24",
    },
    {
      label: "이벤트 기대 + 옵션 프리미엄",
      detail: "행사 직전에는 옵션 프리미엄 확대와 거래량 증가가 함께 나타났다.",
      tone: "neutral",
      relatedDate: "2026-03-21",
    },
  ],
};

export function buildHistoryFixture(symbol = historyFixture.symbol): HistoryFixture {
  return {
    ...historyFixture,
    symbol: symbol.toUpperCase(),
  };
}
