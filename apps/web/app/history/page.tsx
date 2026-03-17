import { HistoryPage } from "@/features/history/components/history-page";
import { getHistoryReplay } from "@/features/history/lib/get-history-replay";

export default async function HistoryRoute() {
  const historyReplay = await getHistoryReplay();

  return <HistoryPage history={historyReplay} />;
}
