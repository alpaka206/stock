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

  return <StockDetailPage stock={stockData} />;
}
