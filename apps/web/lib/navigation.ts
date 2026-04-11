import {
  History,
  LayoutDashboard,
  LineChart,
  Table2,
  type LucideIcon,
} from "lucide-react";

export type NavigationSection = "overview" | "radar" | "stocks" | "history";

export type NavigationItem = {
  id: NavigationSection;
  href: string;
  label: string;
  eyebrow: string;
  description: string;
  icon: LucideIcon;
  matchPrefixes: string[];
};

export type RouteContext = {
  activeSection: NavigationSection;
  label: string;
  eyebrow: string;
  description: string;
};

export const mainNavigation: NavigationItem[] = [
  {
    id: "overview",
    href: "/overview",
    label: "시황 대시보드",
    eyebrow: "시장 스냅샷",
    description: "지수, 뉴스, 섹터 강도, 리스크를 10초 안에 읽는 시작 화면입니다.",
    icon: LayoutDashboard,
    matchPrefixes: ["/overview"],
  },
  {
    id: "radar",
    href: "/radar",
    label: "레이더",
    eyebrow: "관심 종목",
    description: "관심 종목 grid와 섹터 인텔리전스를 한 화면에서 봅니다.",
    icon: Table2,
    matchPrefixes: ["/radar"],
  },
  {
    id: "stocks",
    href: "/stocks/NVDA",
    label: "종목 분석",
    eyebrow: "종목 워크스테이션",
    description: "차트, 수급, 점수, 옵션과 공매도 맥락을 한 흐름으로 읽습니다.",
    icon: LineChart,
    matchPrefixes: ["/stocks"],
  },
  {
    id: "history",
    href: "/history",
    label: "히스토리 리플레이",
    eyebrow: "과거 이벤트",
    description: "과거 급등락과 이벤트 반응을 다시 읽는 화면입니다.",
    icon: History,
    matchPrefixes: ["/history"],
  },
];

const auxiliaryRouteContexts: Array<{ prefixes: string[]; context: RouteContext }> = [
  {
    prefixes: ["/news"],
    context: {
      activeSection: "overview",
      label: "뉴스 피드",
      eyebrow: "뉴스 / 요약",
      description: "해외 속보, 관심종목 뉴스, 국내 공시를 한 흐름으로 보는 보조 화면입니다.",
    },
  },
  {
    prefixes: ["/calendar"],
    context: {
      activeSection: "overview",
      label: "이벤트 캘린더",
      eyebrow: "일정 / 실적",
      description: "실적, IPO, 국내 공시, 뉴스 체크 포인트를 한 화면에서 보는 보조 화면입니다.",
    },
  },
];

function isPrefixMatch(pathname: string, prefixes: string[]) {
  return prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export function getCurrentRouteContext(pathname: string): RouteContext {
  const auxiliary = auxiliaryRouteContexts.find((item) =>
    isPrefixMatch(pathname, item.prefixes)
  );

  if (auxiliary) {
    return auxiliary.context;
  }

  const navigationItem =
    mainNavigation.find((item) => isPrefixMatch(pathname, item.matchPrefixes)) ??
    mainNavigation[0];

  return {
    activeSection: navigationItem.id,
    label: navigationItem.label,
    eyebrow: navigationItem.eyebrow,
    description: navigationItem.description,
  };
}

export function isNavigationActive(pathname: string, navigationItem: NavigationItem) {
  return getCurrentRouteContext(pathname).activeSection === navigationItem.id;
}

export function getCurrentNavigation(pathname: string) {
  const context = getCurrentRouteContext(pathname);
  return mainNavigation.find((item) => item.id === context.activeSection) ?? mainNavigation[0];
}
