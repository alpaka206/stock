import type { ReactNode } from "react";

import { AppNavigation } from "@/components/shell/app-navigation";
import { AppTopbar } from "@/components/shell/app-topbar";
import { Badge } from "@/components/ui/badge";
import { surfaceStyles } from "@/lib/tokens";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-[1800px]">
        <aside className="hidden w-[296px] shrink-0 border-r border-sidebar-border/70 px-4 py-5 lg:block">
          <div
            className={cn(
              surfaceStyles.panel,
              "sticky top-5 flex h-[calc(100vh-2.5rem)] flex-col gap-6 bg-sidebar/85 p-4"
            )}
          >
            <div className="space-y-3">
              <Badge
                variant="secondary"
                className="rounded-full border border-border/60 bg-background/70 px-3 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.16em]"
              >
                AI Research
              </Badge>
              <div>
                <h2 className="text-xl font-semibold tracking-tight">
                  Stock Workspace
                </h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  뉴스, 차트, 섹터, 수급, 점수를 같은 문맥으로 읽는 금융
                  리서치 shell
                </p>
              </div>
            </div>

            <AppNavigation />

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
