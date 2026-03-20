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
