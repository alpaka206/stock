import type { Metadata } from "next";
import { Suspense } from "react";

import { StockDetailPage } from "@/features/stocks/components/stock-detail-page";
import { getStockWorkstation } from "@/features/stocks/lib/get-stock-workstation";

type StockRouteProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export async function generateMetadata({
  params,
}: StockRouteProps): Promise<Metadata> {
  const { symbol } = await params;
  const normalizedSymbol = decodeURIComponent(symbol).toUpperCase();

  return {
    title: `${normalizedSymbol} 종목 분석`,
    description: `${normalizedSymbol} 가격 차트, 기술적 신호, 뉴스, 공시, 이벤트 히스토리를 확인합니다.`,
  };
}

export default async function StockRoute({ params }: StockRouteProps) {
  const { symbol } = await params;
  const stockData = await getStockWorkstation(symbol);

  return (
    <Suspense
      fallback={
        <div className="p-6 text-sm text-muted-foreground">
          종목 분석 화면을 불러오는 중입니다.
        </div>
      }
    >
      <StockDetailPage stock={stockData} />
    </Suspense>
  );
}
