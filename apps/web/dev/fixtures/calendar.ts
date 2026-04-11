import type { CalendarFixture } from "@/lib/research/types";

export const calendarFixture: CalendarFixture = {
  asOf: "04.08 09:20",
  summary:
    "실적, IPO, 국내 공시를 한 흐름으로 보는 샘플 캘린더입니다.",
  highlights: [
    {
      label: "관심종목 실적",
      value: "2건",
      detail: "NVDA, AVGO",
      tone: "positive",
    },
    {
      label: "IPO 캘린더",
      value: "1건",
      detail: "미국 신규 상장 체크",
      tone: "neutral",
    },
    {
      label: "국내 공시",
      value: "1건",
      detail: "OpenDART 연동 전 샘플",
      tone: "neutral",
    },
  ],
  watchlistEvents: [
    {
      id: "fixture-watchlist-event-1",
      title: "NVDA 실적 예정",
      category: "earnings",
      market: "watchlist",
      date: "2026-04-18",
      time: "예정",
      summary: "관심종목 실적 체크 예시입니다.",
      source: "fixture",
      symbol: "NVDA",
      url: "",
      tone: "neutral",
    },
  ],
  marketEvents: [
    {
      id: "fixture-market-event-1",
      title: "Sample IPO",
      category: "ipo",
      market: "global",
      date: "2026-04-22",
      time: "NASDAQ",
      summary: "글로벌 IPO 일정 예시입니다.",
      source: "fixture",
      symbol: "SAMP",
      url: "",
      tone: "neutral",
    },
  ],
  domesticEvents: [
    {
      id: "fixture-domestic-event-1",
      title: "국내 공시 예시",
      category: "disclosure",
      market: "domestic",
      date: "2026-04-17",
      time: "공시",
      summary: "OpenDART 연동 전 샘플 카드입니다.",
      source: "fixture",
      symbol: "005930",
      url: "",
      tone: "neutral",
    },
  ],
  dataSource: {
    mode: "fixture",
    label: "샘플 데이터",
    description: "API가 연결되지 않은 환경에서 캘린더 구조를 먼저 확인하기 위한 fixture입니다.",
  },
};
