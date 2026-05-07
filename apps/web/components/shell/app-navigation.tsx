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
  const sectionLabel = language === "en" ? "Core Screens" : "핵심 화면";

  return (
    <nav className="grid gap-1">
      <div className="mb-3 flex items-center justify-between border-b border-border/80 pb-3 text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground/80">
        <span>{sectionLabel}</span>
        <span className="numeric">{mainNavigation.length}</span>
      </div>

      {mainNavigation.map((navigationItem, index) => {
        const active = routeContext.activeSection === navigationItem.id;

        return (
          <Link
            key={navigationItem.id}
            href={navigationItem.href}
            onClick={onNavigate}
            className={cn(
              "group border-l-2 px-0 py-3 transition-colors",
              active
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:border-border hover:text-foreground"
            )}
          >
            <div
              className={cn(
                "flex items-start justify-between gap-4 border-b border-border/60 pl-3 pb-3",
                active ? "border-border/90" : "group-hover:border-border/85"
              )}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="numeric text-[0.72rem] font-semibold text-muted-foreground/70">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <p className="text-sm font-semibold tracking-tight">
                    {navigationItem.label}
                  </p>
                </div>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {navigationItem.description}
                </p>
              </div>
              <span
                className={cn(
                  "numeric shrink-0 text-[0.72rem] font-semibold",
                  active ? "text-primary" : "text-muted-foreground/60"
                )}
              >
                {navigationItem.id.toUpperCase()}
              </span>
            </div>
          </Link>
        );
      })}
    </nav>
  );
}
