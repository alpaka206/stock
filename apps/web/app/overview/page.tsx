import { OverviewPage } from "@/features/overview/components/overview-page";
import { getOverviewSnapshot } from "@/features/overview/lib/get-overview-snapshot";

export const dynamic = "force-dynamic";

export default async function OverviewRoute() {
  const overviewData = await getOverviewSnapshot();

  return <OverviewPage data={overviewData} />;
}
