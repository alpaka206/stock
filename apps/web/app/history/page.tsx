import { Suspense } from "react";

import { HistoryPage } from "@/features/history/components/history-page";
import { getHistoryReplay } from "@/features/history/lib/get-history-replay";

export const metadata = {
  title: "이벤트 히스토리",
  description: "종목의 과거 급등락과 뉴스, 공시, 실적 이벤트를 차트와 함께 복기합니다.",
};

type HistoryRouteProps = {
  searchParams: Promise<{
    symbol?: string;
    range?: string;
    from?: string;
    to?: string;
  }>;
};

export default async function HistoryRoute({ searchParams }: HistoryRouteProps) {
  const params = await searchParams;
  const historyReplay = await getHistoryReplay(params);

  return (
    <Suspense
      fallback={
        <div className="p-6 text-sm text-muted-foreground">
          히스토리 화면을 불러오는 중입니다.
        </div>
      }
    >
      <HistoryPage history={historyReplay} />
    </Suspense>
  );
}
