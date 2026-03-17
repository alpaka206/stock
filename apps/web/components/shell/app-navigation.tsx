"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { mainNavigation, isNavigationActive } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type AppNavigationProps = {
  onNavigate?: () => void;
};

export function AppNavigation({ onNavigate }: AppNavigationProps) {
  const pathname = usePathname();

  return (
    <nav className="grid gap-2">
      {mainNavigation.map((navigationItem) => {
        const active = isNavigationActive(pathname, navigationItem);
        const Icon = navigationItem.icon;

        return (
          <Link
            key={navigationItem.id}
            href={navigationItem.href}
            onClick={onNavigate}
            className={cn(
              "group rounded-[calc(var(--radius)*1.15)] border border-transparent px-3 py-3 transition-colors",
              active
                ? "border-primary/30 bg-primary/10 text-foreground"
                : "hover:border-border/70 hover:bg-background/55"
            )}
          >
            <div className="flex items-start gap-3">
              <div
                className={cn(
                  "mt-0.5 rounded-xl border p-2",
                  active
                    ? "border-primary/35 bg-primary/15 text-primary"
                    : "border-border/70 bg-background/70 text-muted-foreground"
                )}
              >
                <Icon className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold tracking-tight">
                    {navigationItem.label}
                  </p>
                  {navigationItem.id === "stocks" ? (
                    <Badge
                      variant="secondary"
                      className="rounded-full px-2 py-0.5 text-[0.68rem]"
                    >
                      샘플
                    </Badge>
                  ) : null}
                </div>
                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                  {navigationItem.description}
                </p>
              </div>
            </div>
          </Link>
        );
      })}
    </nav>
  );
}
