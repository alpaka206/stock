"use client";

import * as React from "react";
import { Menu } from "lucide-react";
import { usePathname } from "next/navigation";

import { AppNavigation } from "@/components/shell/app-navigation";
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
  const routeContext = getCurrentRouteContext(pathname);
  const [open, setOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-border/60 bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-[1600px] items-center justify-between gap-4 px-[var(--space-page)] lg:px-[var(--space-page-lg)]">
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
                <span className="sr-only">메뉴 열기</span>
              </Button>
            </SheetTrigger>
            <SheetContent
              side="left"
              className="w-[min(88vw,340px)] border-r border-border/60 bg-background/95 p-0"
            >
              <SheetHeader className="border-b border-border/60 pb-4">
                <SheetTitle>리서치 워크스페이스</SheetTitle>
                <SheetDescription>
                  메인 4개 화면을 빠르게 오가며 리서치 흐름을 이어갑니다.
                </SheetDescription>
              </SheetHeader>
              <div className="p-4">
                <AppNavigation onNavigate={() => setOpen(false)} />
              </div>
            </SheetContent>
          </Sheet>

          <div className="min-w-0">
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              {routeContext.eyebrow}
            </p>
            <h1 className="truncate text-lg font-semibold tracking-tight">
              {routeContext.label}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant="secondary"
            className="hidden rounded-full border border-border/60 bg-background/75 px-3 py-1 text-[0.72rem] font-medium text-muted-foreground sm:inline-flex"
          >
            리서치 워크스페이스
          </Badge>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
