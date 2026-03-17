import type { OverviewFixture } from "@/lib/research/types";

export const overviewFixture: OverviewFixture = {
  asOf: "2026-03-16 08:40 KST",
  lead:
    "미국 대형 기술주 강세가 유지되지만 반도체와 소프트웨어의 탄력 차이가 커지고 있다. 오늘 화면은 AI 인프라 우위와 장기 금리 부담을 같이 읽도록 설계했다.",
  scenario:
    "우선검토 섹터는 반도체 장비와 전력 인프라다. 금리 재상승이 재개되면 고밸류 성장주의 탄성은 빠르게 약화될 수 있다.",
  indices: [
    {
      name: "NASDAQ 100",
      symbol: "NDX",
      value: 20184.72,
      changePercent: 1.28,
      note: "반도체·클라우드 동시 강세",
    },
    {
      name: "S&P 500",
      symbol: "SPX",
      value: 5481.16,
      changePercent: 0.64,
      note: "대형주 중심 완만한 확산",
    },
    {
      name: "필라델피아 반도체",
      symbol: "SOX",
      value: 5150.81,
      changePercent: 2.14,
      note: "장비·메모리 추세 유지",
    },
    {
      name: "미 10년물 금리",
      symbol: "US10Y",
      value: 4.18,
      changePercent: -0.36,
      note: "성장주 부담 완화",
    },
  ],
  news: [
    {
      id: "overview-news-1",
      source: "시장 요약",
      headline: "AI 서버 공급망 가이던스 상향이 장 초반 리스크 선호를 유지",
      summary:
        "GPU, 네트워크, 전력장비 수요가 한 흐름으로 묶이며 장비주까지 수급이 확산됐다.",
      publishedAt: "07:55",
      impactLabel: "우선검토",
      tone: "positive",
    },
    {
      id: "overview-news-2",
      source: "매크로 체크",
      headline: "장기 금리 재반등 가능성은 아직 남아 있어 밸류에이션 확장은 제한적",
      summary:
        "지표 발표 전까지는 고점 추격보다 섹터 내부 상대강도 비교가 더 중요하다.",
      publishedAt: "08:05",
      impactLabel: "조건부 강세",
      tone: "neutral",
    },
    {
      id: "overview-news-3",
      source: "섹터 메모",
      headline: "사이버보안은 실적 시즌 전 방어적 성장 바스켓으로 재부각",
      summary:
        "실적 변동성이 낮고 대형 고객사 갱신 모멘텀이 확인되는 종목군에 수급이 붙고 있다.",
      publishedAt: "08:18",
      impactLabel: "관심",
      tone: "positive",
    },
  ],
  sectors: [
    {
      id: "semi",
      name: "반도체 장비",
      score: 87,
      changePercent: 2.3,
      direction: "up",
      momentum: "실적 상향과 CAPEX 확대가 동시에 진행 중",
      catalysts: ["AI 서버 증설", "메모리 회복", "장비주 밸류 재평가"],
    },
    {
      id: "power",
      name: "전력 인프라",
      score: 79,
      changePercent: 1.5,
      direction: "up",
      momentum: "데이터센터 전력 수요가 구조적 테마로 이동",
      catalysts: ["변압기 공급 부족", "전력망 투자 확대", "장기 수주 visibility"],
    },
    {
      id: "software",
      name: "엔터프라이즈 소프트웨어",
      score: 67,
      changePercent: 0.6,
      direction: "flat",
      momentum: "가이던스는 견조하지만 금리 민감도가 남아 있음",
      catalysts: ["생성형 AI 번들링", "마진 방어", "대형 고객 업셀"],
    },
    {
      id: "consumer",
      name: "소비재",
      score: 42,
      changePercent: -0.7,
      direction: "down",
      momentum: "가격 전가 피로와 경기 민감도 상승",
      catalysts: ["재고 조정", "소비 둔화", "환율 부담"],
    },
  ],
  risks: [
    {
      label: "금리 민감도",
      value: "중간",
      detail: "10년물 4.3% 재돌파 시 성장주 압축 가능성",
      tone: "neutral",
    },
    {
      label: "실적 기대 과열",
      value: "높음",
      detail: "AI 공급망 상단 종목은 가이던스 미스에 민감",
      tone: "negative",
    },
    {
      label: "섹터 로테이션",
      value: "낮음",
      detail: "현재는 순환보다 상단 테마 집중이 강한 구간",
      tone: "positive",
    },
  ],
  heatmap: [
    { label: "반도체", score: 91, changePercent: 2.4 },
    { label: "보안", score: 76, changePercent: 1.2 },
    { label: "전력", score: 81, changePercent: 1.6 },
    { label: "클라우드", score: 69, changePercent: 0.8 },
    { label: "바이오", score: 48, changePercent: -0.4 },
    { label: "소비재", score: 39, changePercent: -0.8 },
  ],
};
