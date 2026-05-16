import type { NewsFeedFixture } from "@/lib/research/types";

export const newsFeedFixture: NewsFeedFixture = {
  asOf: "05.16 09:10",
  marketSummary:
    "뉴스 API가 연결되기 전 화면 구조를 확인하기 위한 뉴스 피드입니다. 모든 항목은 실제 데이터가 아니며 제목과 요약에 (목데이터)를 표시합니다.",
  drivers: [
    {
      label: "해외 헤드라인",
      text: "미국 주요 지수와 대형 기술주 흐름을 먼저 확인하는 영역입니다. (목데이터)",
      tone: "neutral",
      href: "/overview",
    },
    {
      label: "관심종목",
      text: "레이더에 담은 종목과 직접 연결되는 기사만 따로 분리합니다. (목데이터)",
      tone: "neutral",
      href: "/radar",
    },
    {
      label: "국내 공시",
      text: "OpenDART 연결 전까지 공시 카드 위치와 이동 흐름을 확인합니다. (목데이터)",
      tone: "neutral",
      href: "/calendar",
    },
  ],
  featuredNews: [
    {
      id: "fixture-global-1",
      headline: "AI 서버 투자 기대가 반도체 대표주에 반영되는 흐름 (목데이터)",
      source: "목데이터",
      summary: "실제 해외 뉴스 API 연결 전 레이아웃과 종목 이동 흐름을 확인하기 위한 기사입니다. (목데이터)",
      impact: "점검",
      publishedAt: "2026-05-16T09:10:00+09:00",
      url: "",
      symbol: "NVDA",
      market: "global",
    },
  ],
  watchlistNews: [
    {
      id: "fixture-watchlist-1",
      headline: "관심종목 중심 뉴스 카드 예시 (목데이터)",
      source: "목데이터",
      summary: "사용자가 저장한 종목과 바로 연결되는 뉴스 영역을 검증하기 위한 항목입니다. (목데이터)",
      impact: "확인 필요",
      publishedAt: "2026-05-16T09:25:00+09:00",
      url: "",
      symbol: "AVGO",
      market: "watchlist",
    },
  ],
  domesticDisclosures: [
    {
      id: "fixture-domestic-1",
      headline: "국내 공시 카드 예시 (목데이터)",
      source: "목데이터",
      summary: "OpenDART 연동 전 국내 공시 목록과 외부 원문 링크 위치를 확인하기 위한 항목입니다. (목데이터)",
      impact: "공시",
      publishedAt: "2026-05-16T08:30:00+09:00",
      url: "",
      symbol: "005930",
      market: "domestic",
    },
  ],
  dataSource: {
    mode: "fixture",
    label: "기본 데이터 (목데이터)",
    description:
      "뉴스 API가 연결되지 않은 환경에서 화면 구조를 확인하기 위한 목데이터입니다.",
  },
};
