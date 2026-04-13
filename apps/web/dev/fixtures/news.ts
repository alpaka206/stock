import type { NewsFeedFixture } from "@/lib/research/types";

export const newsFeedFixture: NewsFeedFixture = {
  asOf: "04.08 09:10",
  marketSummary:
    "해외 헤드라인, 관심종목 뉴스, 국내 공시를 한 흐름으로 읽는 뉴스 피드입니다.",
  drivers: [
    {
      label: "해외 헤드라인",
      text: "메인 헤드라인을 먼저 읽고 세부 종목 반응으로 내려갑니다.",
      tone: "positive",
      href: "/overview",
    },
    {
      label: "관심종목",
      text: "레이더 종목과 연동되는 뉴스를 분리해 봅니다.",
      tone: "neutral",
      href: "/radar",
    },
    {
      label: "국내 공시",
      text: "OpenDART 연동 전까지는 기본 공시 카드를 표시합니다.",
      tone: "neutral",
      href: "/calendar",
    },
  ],
  featuredNews: [
    {
      id: "fixture-global-1",
      headline: "AI 서버 투자 기대가 반도체 대형주 강세를 유지했습니다.",
      source: "fixture",
      summary: "해외 메인 흐름을 보기 위한 예시 카드입니다.",
      impact: "긍정",
      publishedAt: "2026-04-08T00:10:00+09:00",
      url: "",
      symbol: "NVDA",
      market: "global",
    },
  ],
  watchlistNews: [
    {
      id: "fixture-watchlist-1",
      headline: "관심종목 중심 뉴스 흐름을 따로 추린다.",
      source: "fixture",
      summary: "레이더와 종목 화면으로 바로 이동할 수 있는 예시입니다.",
      impact: "관심",
      publishedAt: "2026-04-08T00:25:00+09:00",
      url: "",
      symbol: "AVGO",
      market: "watchlist",
    },
  ],
  domesticDisclosures: [
    {
      id: "fixture-domestic-1",
      headline: "국내 공시 예시",
      source: "fixture",
      summary: "OpenDART 연동 전 기본 공시 카드입니다.",
      impact: "공시",
      publishedAt: "2026-04-08T08:30:00+09:00",
      url: "",
      symbol: "005930",
      market: "domestic",
    },
  ],
  dataSource: {
    mode: "fixture",
    label: "기본 데이터",
    description: "API가 연결되지 않은 환경에서 뉴스 피드 구조를 먼저 확인하기 위한 fixture입니다.",
  },
};
