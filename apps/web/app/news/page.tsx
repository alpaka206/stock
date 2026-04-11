import { Suspense } from "react";

import { NewsFeedPage } from "@/features/news/components/news-feed-page";
import { getNewsFeed } from "@/features/news/lib/get-news-feed";

type NewsRouteProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function NewsRoute({ searchParams }: NewsRouteProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const rawScope = resolvedSearchParams.scope;
  const scope = typeof rawScope === "string" ? rawScope : "all";
  const newsFeed = await getNewsFeed();

  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">뉴스 피드를 불러오는 중입니다.</div>}>
      <NewsFeedPage data={newsFeed} scope={scope} />
    </Suspense>
  );
}
