import "server-only";

import { newsFeedFixture } from "@/dev/fixtures/news";
import {
  allowFixtureFallback,
  assertResearchApiAvailable,
  assertResearchApiConfigured,
  buildFixtureDataSource,
  buildPayloadDataSource,
  fetchResearchApiJson,
} from "@/lib/server/research-api";
import type { NewsApiResponse, NewsFeedFixture, OverviewDriverItem } from "@/lib/research/types";

export async function getNewsFeed() {
  const result = await fetchResearchApiJson<NewsApiResponse>({
    explicitUrlEnv: "NEWS_API_URL",
    basePath: "/news",
  });

  if (result.status === "disabled") {
    assertResearchApiConfigured(result, "news");
    return {
      ...newsFeedFixture,
      dataSource: buildFixtureDataSource({
        fallback: false,
        reason: "API URL이 설정되지 않아 샘플 뉴스 피드를 표시합니다.",
      }),
    } satisfies NewsFeedFixture;
  }

  if (result.status === "error") {
    assertResearchApiAvailable(result, "news");
    return {
      ...newsFeedFixture,
      dataSource: buildFixtureDataSource({
        fallback: allowFixtureFallback(),
        reason: `news API 연결이 실패해 샘플 뉴스 피드를 대신 표시합니다. ${result.errorMessage}`,
      }),
    } satisfies NewsFeedFixture;
  }

  const payload = result.payload;
  const hasData =
    payload.featuredNews.length > 0 ||
    payload.watchlistNews.length > 0 ||
    payload.domesticDisclosures.length > 0;

  if (!hasData) {
    return {
      ...newsFeedFixture,
      dataSource: buildFixtureDataSource({
        fallback: true,
        reason: "news API 응답에 표시할 뉴스가 없어 fixture를 대신 사용합니다.",
      }),
    } satisfies NewsFeedFixture;
  }

  return {
    asOf: formatAsOf(payload.asOf),
    marketSummary: payload.marketSummary.text,
    drivers: mapDrivers(payload),
    featuredNews: payload.featuredNews,
    watchlistNews: payload.watchlistNews,
    domesticDisclosures: payload.domesticDisclosures,
    dataSource: buildPayloadDataSource(payload.sourceRefs),
  } satisfies NewsFeedFixture;
}

function mapDrivers(payload: NewsApiResponse): OverviewDriverItem[] {
  const labels = ["해외 헤드라인", "관심종목", "국내 공시"] as const;
  const tones = ["positive", "neutral", "neutral"] as const;
  const hrefs = ["/overview", "/radar", "/calendar"] as const;

  return payload.newsDrivers.slice(0, 3).map((item, index) => ({
    label: labels[index] ?? `포인트 ${index + 1}` ,
    text: item.text,
    tone: tones[index] ?? "neutral",
    href: hrefs[index] ?? "/overview",
  }));
}

function formatAsOf(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return newsFeedFixture.asOf;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
