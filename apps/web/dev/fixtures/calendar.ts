import type { CalendarFixture } from "@/lib/research/types";

export const calendarFixture: CalendarFixture = {
  asOf: "05.16 09:20",
  summary:
    "일정 API가 연결되기 전 실적, IPO, 국내 공시를 한 화면에서 확인하는 흐름을 검증하기 위한 캘린더입니다. 모든 항목은 (목데이터)입니다.",
  highlights: [
    {
      label: "관심종목 실적",
      value: "2건",
      detail: "NVDA, AVGO 일정 카드 예시 (목데이터)",
      tone: "neutral",
    },
    {
      label: "IPO 캘린더",
      value: "1건",
      detail: "미국 신규 상장 체크 예시 (목데이터)",
      tone: "neutral",
    },
    {
      label: "국내 공시",
      value: "1건",
      detail: "OpenDART 연동 전 기본 카드 (목데이터)",
      tone: "neutral",
    },
  ],
  watchlistEvents: [
    {
      id: "fixture-watchlist-event-1",
      title: "NVDA 실적 발표 예정 (목데이터)",
      category: "earnings",
      market: "watchlist",
      date: "2026-05-20",
      time: "예정",
      summary: "관심종목 실적 체크 화면을 검증하기 위한 일정입니다. (목데이터)",
      source: "목데이터",
      symbol: "NVDA",
      url: "",
      tone: "neutral",
    },
  ],
  marketEvents: [
    {
      id: "fixture-market-event-1",
      title: "신규 상장 일정 예시 (목데이터)",
      category: "ipo",
      market: "global",
      date: "2026-05-22",
      time: "NASDAQ",
      summary: "글로벌 IPO 일정 카드 레이아웃을 확인하기 위한 항목입니다. (목데이터)",
      source: "목데이터",
      symbol: "SAMP",
      url: "",
      tone: "neutral",
    },
  ],
  domesticEvents: [
    {
      id: "fixture-domestic-event-1",
      title: "국내 공시 일정 예시 (목데이터)",
      category: "disclosure",
      market: "domestic",
      date: "2026-05-17",
      time: "공시",
      summary: "OpenDART 연동 전 국내 공시 흐름을 확인하기 위한 항목입니다. (목데이터)",
      source: "목데이터",
      symbol: "005930",
      url: "",
      tone: "neutral",
    },
  ],
  dataSource: {
    mode: "fixture",
    label: "기본 데이터 (목데이터)",
    description:
      "일정 API가 연결되지 않은 환경에서 캘린더 구조를 확인하기 위한 목데이터입니다.",
  },
};
