import {
  History,
  LayoutDashboard,
  LineChart,
  Table2,
  type LucideIcon,
} from "lucide-react";

import type { AppLanguage } from "@/lib/i18n/messages";
import { getMessages } from "@/lib/i18n/messages";

export type NavigationSection = "overview" | "radar" | "stocks" | "history";

export type NavigationItem = {
  id: NavigationSection;
  href: string;
  icon: LucideIcon;
  matchPrefixes: string[];
};

export type RouteContext = {
  activeSection: NavigationSection;
  label: string;
  eyebrow: string;
  description: string;
};

const mainNavigationBase: NavigationItem[] = [
  {
    id: "overview",
    href: "/overview",
    icon: LayoutDashboard,
    matchPrefixes: ["/overview"],
  },
  {
    id: "radar",
    href: "/radar",
    icon: Table2,
    matchPrefixes: ["/radar"],
  },
  {
    id: "stocks",
    href: "/stocks/NVDA",
    icon: LineChart,
    matchPrefixes: ["/stocks"],
  },
  {
    id: "history",
    href: "/history",
    icon: History,
    matchPrefixes: ["/history"],
  },
];

const auxiliaryRouteContexts: Array<{
  id: "news" | "calendar";
  prefixes: string[];
  activeSection: NavigationSection;
}> = [
  {
    id: "news",
    prefixes: ["/news"],
    activeSection: "overview",
  },
  {
    id: "calendar",
    prefixes: ["/calendar"],
    activeSection: "overview",
  },
];

function isPrefixMatch(pathname: string, prefixes: string[]) {
  return prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export function getMainNavigation(language: AppLanguage) {
  const messages = getMessages(language);

  return mainNavigationBase.map((item) => ({
    ...item,
    ...messages.navigation.main[item.id],
  }));
}

export function getCurrentRouteContext(
  pathname: string,
  language: AppLanguage
): RouteContext {
  const messages = getMessages(language);
  const auxiliary = auxiliaryRouteContexts.find((item) =>
    isPrefixMatch(pathname, item.prefixes)
  );

  if (auxiliary) {
    return {
      activeSection: auxiliary.activeSection,
      ...messages.navigation.auxiliary[auxiliary.id],
    };
  }

  const navigationItem =
    mainNavigationBase.find((item) => isPrefixMatch(pathname, item.matchPrefixes)) ??
    mainNavigationBase[0];

  return {
    activeSection: navigationItem.id,
    ...messages.navigation.main[navigationItem.id],
  };
}

export function isNavigationActive(
  pathname: string,
  navigationItem: NavigationItem
) {
  return getCurrentRouteContext(pathname, "ko").activeSection === navigationItem.id;
}
