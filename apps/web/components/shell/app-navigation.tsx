"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAppLanguage } from "@/components/providers/language-provider";
import { getCurrentRouteContext, getMainNavigation } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type AppNavigationProps = {
  onNavigate?: () => void;
};

export function AppNavigation({ onNavigate }: AppNavigationProps) {
  const pathname = usePathname();
  const { language } = useAppLanguage();
  const routeContext = getCurrentRouteContext(pathname, language);
  const mainNavigation = getMainNavigation(language);
  const sectionLabel =
    language === "en"
      ? "Core views"
      : language === "ja"
        ? "主要画面"
        : language === "zh"
          ? "主要页面"
          : "핵심 화면";

  return (
    <nav className="grid gap-1">
      <div className="mb-2 flex items-center justify-between border-b border-border/80 pb-3 text-xs font-semibold uppercase text-muted-foreground">
        <span>{sectionLabel}</span>
        <span className="numeric">{mainNavigation.length}</span>
      </div>

      {mainNavigation.map((navigationItem) => {
        const active = routeContext.activeSection === navigationItem.id;
        const Icon = navigationItem.icon;

        return (
          <Link
            key={navigationItem.id}
            href={navigationItem.href}
            onClick={onNavigate}
            className={cn(
              "group flex items-start gap-3 rounded-md border px-3 py-3 transition-colors",
              active
                ? "border-primary/35 bg-primary/10 text-foreground"
                : "border-transparent text-muted-foreground hover:border-border hover:bg-muted/40 hover:text-foreground"
            )}
          >
            <span
              className={cn(
                "mt-0.5 inline-flex size-8 shrink-0 items-center justify-center rounded-md border",
                active
                  ? "border-primary/30 bg-background/60 text-primary"
                  : "border-border/70 bg-background/45 text-muted-foreground"
              )}
            >
              <Icon className="size-4" />
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-semibold tracking-normal">
                {navigationItem.label}
              </span>
              <span className="mt-1 block text-xs leading-5 text-muted-foreground">
                {navigationItem.description}
              </span>
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
