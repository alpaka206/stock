import type { HistoryFixture } from "@/lib/research/types";

export const historyFixture: HistoryFixture = {
  symbol: "NVDA",
  range: "2025-10-01 ~ 2026-03-16",
  presets: ["1개월", "3개월", "6개월", "이벤트 구간"],
  chartPoints: [
    { label: "10/01", close: 612, volume: 38 },
    { label: "10/22", close: 648, volume: 42 },
    { label: "11/12", close: 701, volume: 47 },
    { label: "12/03", close: 736, volume: 44 },
    { label: "12/24", close: 718, volume: 36 },
    { label: "01/14", close: 782, volume: 58 },
    { label: "02/04", close: 835, volume: 62 },
    { label: "02/25", close: 881, volume: 64 },
    { label: "03/16", close: 923, volume: 57 },
  ],
  events: [
    {
      id: "history-event-1",
      date: "2025-10-18",
      title: "AI 서버 수주 상향",
      category: "섹터",
      summary: "공급망 전반 수주 상향이 확인되며 테마 리더십이 강화됐다.",
      reaction: "3주간 +11%",
      tone: "positive",
    },
    {
      id: "history-event-2",
      date: "2025-12-12",
      title: "장기 금리 급반등",
      category: "매크로",
      summary: "고밸류 성장주 밸류에이션 압축으로 조정 폭이 커졌다.",
      reaction: "2주간 -6%",
      tone: "negative",
    },
    {
      id: "history-event-3",
      date: "2026-01-29",
      title: "가이던스 재상향",
      category: "실적",
      summary: "출하량 전망 상향으로 조정 이후 추세가 재개됐다.",
      reaction: "4주간 +13%",
      tone: "positive",
    },
    {
      id: "history-event-4",
      date: "2026-03-11",
      title: "이벤트 기대 확산",
      category: "이벤트",
      summary: "키노트 기대감이 옵션 프리미엄과 거래량 확대로 연결됐다.",
      reaction: "5일간 +4.8%",
      tone: "neutral",
    },
  ],
  moveReasons: [
    {
      label: "상승 구간 핵심 이유",
      description: "공급망 상향과 실적 가이던스 개선이 겹치며 멀티플 확장이 허용됐다.",
      tone: "positive",
    },
    {
      label: "조정 구간 핵심 이유",
      description: "금리 급반등 때 밸류 부담이 한 번에 노출됐다.",
      tone: "negative",
    },
    {
      label: "현재 해석",
      description: "이벤트 기대가 강하지만 과열 영역에 가까워 확인 이후 반응을 같이 봐야 한다.",
      tone: "neutral",
    },
  ],
  overlaps: [
    {
      label: "거래량 + 모멘텀",
      detail: "가이던스 상향 시점에 거래량과 상대강도가 동시에 확대",
      tone: "positive",
    },
    {
      label: "금리 + 밸류 압축",
      detail: "금리 급반등 구간에는 차트 지지선 이탈이 동반",
      tone: "negative",
    },
    {
      label: "이벤트 프리미엄",
      detail: "이벤트 직전에는 옵션 프리미엄이 먼저 확대되는 패턴",
      tone: "neutral",
    },
  ],
};
