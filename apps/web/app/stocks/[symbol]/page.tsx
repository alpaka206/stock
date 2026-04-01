import { Suspense } from "react";

import { StockDetailPage } from "@/features/stocks/components/stock-detail-page";
import { getStockWorkstation } from "@/features/stocks/lib/get-stock-workstation";

type StockRouteProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default async function StockRoute({ params }: StockRouteProps) {
  const { symbol } = await params;
  const stockData = await getStockWorkstation(symbol);

  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">종목 워크스테이션을 불러오는 중입니다.</div>}>
      <StockDetailPage stock={stockData} />
    </Suspense>
  );
}
