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

export const mainNavigation: NavigationItem[] = [
  {
    id: "overview",
    href: "/overview",
    label: "개요 대시보드",
    eyebrow: "Overview",
    description: "지수, 뉴스, 섹터 강도, 리스크를 한 번에 훑는다.",
    icon: LayoutDashboard,
    matchPrefixes: ["/overview"],
  },
  {
    id: "radar",
    href: "/radar",
    label: "레이더",
    eyebrow: "Radar",
    description: "관심종목 grid와 섹터 인텔리전스를 함께 본다.",
    icon: Table2,
    matchPrefixes: ["/radar"],
  },
  {
    id: "stocks",
    href: "/stocks/NVDA",
    label: "종목 분석",
    eyebrow: "Stock Detail",
    description: "차트, 수급, 점수, 옵션·공매도를 같은 흐름으로 읽는다.",
    icon: LineChart,
    matchPrefixes: ["/stocks"],
  },
  {
    id: "history",
    href: "/history",
    label: "히스토리 리플레이",
    eyebrow: "History",
    description: "과거 급등락 구간을 이벤트와 함께 되짚는다.",
    icon: History,
    matchPrefixes: ["/history"],
  },
];

export function isNavigationActive(
  pathname: string,
  navigationItem: NavigationItem
) {
  return navigationItem.matchPrefixes.some((prefix) => {
    return pathname === prefix || pathname.startsWith(`${prefix}/`);
  });
}

export function getCurrentNavigation(pathname: string) {
  return (
    mainNavigation.find((navigationItem) =>
      isNavigationActive(pathname, navigationItem)
    ) ?? mainNavigation[0]
  );
}
