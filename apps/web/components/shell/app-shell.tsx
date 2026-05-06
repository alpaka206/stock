"use client";

import type { ReactNode } from "react";

import { useAppLanguage } from "@/components/providers/language-provider";
import { AppNavigation } from "@/components/shell/app-navigation";
import { AppTopbar } from "@/components/shell/app-topbar";
import { Badge } from "@/components/ui/badge";
import { surfaceStyles } from "@/lib/tokens";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: ReactNode }) {
  const { messages } = useAppLanguage();

  return (
    <div className="min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-[1820px]">
        <aside className="hidden w-[312px] shrink-0 border-r border-sidebar-border px-4 py-5 lg:block">
          <div
            className={cn(
              surfaceStyles.panel,
              "sticky top-5 flex h-[calc(100vh-2.5rem)] flex-col bg-sidebar px-4 py-4"
            )}
          >
            <div className="border-b border-border/80 pb-5">
              <p className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-muted-foreground/80">
                {messages.shell.badge}
              </p>
              <div className="mt-3">
                <h2 className="text-[1.35rem] font-semibold tracking-[-0.03em]">
                  {messages.shell.title}
                </h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {messages.shell.description}
                </p>
              </div>
            </div>

            <div className="grid gap-2 border-b border-border/80 py-4 text-[0.72rem] text-muted-foreground">
              <div className="flex items-center justify-between">
                <span className="uppercase tracking-[0.18em]">
                  {messages.shell.coverageLabel}
                </span>
                <span className="numeric font-semibold text-foreground">
                  {messages.shell.coverageValue}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="uppercase tracking-[0.18em]">
                  {messages.shell.modeLabel}
                </span>
                <span className="font-semibold text-foreground">
                  {messages.shell.modeValue}
                </span>
              </div>
            </div>

            <div className="flex-1 pt-4">
              <AppNavigation />
            </div>

            <Badge
              variant="secondary"
              className="justify-center rounded-[0.45rem] border border-border/80 bg-muted/15 px-3 py-2 text-[0.72rem] font-medium text-muted-foreground"
            >
              {messages.shell.footerNote}
            </Badge>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <AppTopbar />
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  );
}
