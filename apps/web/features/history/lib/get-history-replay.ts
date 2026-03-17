import "server-only";

import { historyFixture } from "@/dev/fixtures/history";

export async function getHistoryReplay() {
  return historyFixture;
}
