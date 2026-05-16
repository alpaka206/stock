"use client";

import * as React from "react";
import { Menu } from "lucide-react";
import { usePathname } from "next/navigation";

import { useAppLanguage } from "@/components/providers/language-provider";
import { AppNavigation } from "@/components/shell/app-navigation";
import { LanguageSelect } from "@/components/shell/language-select";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { getCurrentRouteContext } from "@/lib/navigation";

export function AppTopbar() {
  const pathname = usePathname();
  const { language, messages } = useAppLanguage();
  const routeContext = getCurrentRouteContext(pathname, language);
  const [open, setOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-border/80 bg-background/95 backdrop-blur">
      <div className="mx-auto flex min-h-16 w-full max-w-[1680px] items-center justify-between gap-4 px-[var(--space-page)] py-3 lg:px-[var(--space-page-lg)]">
        <div className="flex min-w-0 items-center gap-3">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button
                variant="outline"
                size="icon-sm"
                type="button"
                className="lg:hidden"
              >
                <Menu />
                <span className="sr-only">{messages.topbar.mobileMenuSr}</span>
              </Button>
            </SheetTrigger>
            <SheetContent
              side="left"
              className="w-[min(88vw,340px)] border-r border-border/80 bg-background p-0"
            >
              <SheetHeader className="border-b border-border/60 pb-4">
                <SheetTitle>{messages.topbar.mobileSheetTitle}</SheetTitle>
                <SheetDescription>{messages.topbar.mobileSheetDescription}</SheetDescription>
              </SheetHeader>
              <div className="p-4">
                <div className="mb-4 sm:hidden">
                  <LanguageSelect />
                </div>
                <AppNavigation onNavigate={() => setOpen(false)} />
              </div>
            </SheetContent>
          </Sheet>

          <div className="min-w-0">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase text-muted-foreground">
              <span>{routeContext.eyebrow}</span>
              <span className="inline-block size-1 rounded-full bg-border" />
              <span className="hidden md:inline">{messages.topbar.workflowLabel}</span>
            </div>
            <div className="mt-1 flex min-w-0 items-center gap-3">
              <h1 className="truncate text-lg font-semibold tracking-normal">
                {routeContext.label}
              </h1>
              <p className="hidden truncate text-sm text-muted-foreground xl:block">
                {routeContext.description}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden sm:block">
            <LanguageSelect />
          </div>
          <Badge
            variant="secondary"
            className="hidden rounded-md border border-border/80 bg-muted/20 px-3 py-1.5 text-xs font-medium text-muted-foreground sm:inline-flex"
          >
            {messages.topbar.workspaceBadge}
          </Badge>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
