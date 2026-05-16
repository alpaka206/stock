import { OverviewPage } from "@/features/overview/components/overview-page";
import { getOverviewSnapshot } from "@/features/overview/lib/get-overview-snapshot";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "시장 개요",
  description: "미국장과 국내장의 지수, 섹터, 뉴스, 위험 요인을 한 화면에서 확인합니다.",
};

export default async function OverviewRoute() {
  const overviewData = await getOverviewSnapshot();

  return <OverviewPage data={overviewData} />;
}
