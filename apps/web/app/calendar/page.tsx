import { Suspense } from "react";

import { CalendarBoardPage } from "@/features/calendar/components/calendar-board-page";
import { getCalendarBoard } from "@/features/calendar/lib/get-calendar-board";

type CalendarRouteProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function CalendarRoute({ searchParams }: CalendarRouteProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const rawScope = resolvedSearchParams.scope;
  const scope = typeof rawScope === "string" ? rawScope : "all";
  const calendarBoard = await getCalendarBoard();

  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">캘린더를 불러오는 중입니다.</div>}>
      <CalendarBoardPage data={calendarBoard} scope={scope} />
    </Suspense>
  );
}
