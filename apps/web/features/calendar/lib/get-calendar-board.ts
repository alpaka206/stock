import "server-only";

import { calendarFixture } from "@/dev/fixtures/calendar";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  assertResearchApiConfigured,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type { CalendarApiResponse, CalendarFixture } from "@/lib/research/types";

export async function getCalendarBoard() {
  const result = await fetchResearchApiJson<CalendarApiResponse>({
    explicitUrlEnv: "CALENDAR_API_URL",
    basePath: "/calendar",
  });

  if (result.status === "disabled") {
    assertResearchApiConfigured(result, "calendar");
    return {
      ...calendarFixture,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 기본 일정을 표시합니다.",
      }),
    } satisfies CalendarFixture;
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "calendar");
    return {
      ...calendarFixture,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `calendar API 연결이 실패해 대체 일정을 표시합니다. ${result.errorMessage}`,
      }),
    } satisfies CalendarFixture;
  }

  const payload = result.payload;
  const hasData =
    payload.watchlistEvents.length > 0 ||
    payload.marketEvents.length > 0 ||
    payload.domesticEvents.length > 0;

  if (!hasData) {
    return {
      ...calendarFixture,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "calendar API 응답에 표시할 일정이 없어 기본 일정을 표시합니다.",
      }),
    } satisfies CalendarFixture;
  }

  return {
    asOf: formatAsOf(payload.asOf),
    summary: payload.calendarSummary.text,
    highlights: payload.highlights,
    watchlistEvents: payload.watchlistEvents,
    marketEvents: payload.marketEvents,
    domesticEvents: payload.domesticEvents,
    dataSource: buildPayloadDataSource(payload.sourceRefs),
  } satisfies CalendarFixture;
}

function formatAsOf(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return calendarFixture.asOf;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
