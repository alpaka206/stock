import "server-only";

import { overviewFixture } from "@/dev/fixtures/overview";

export async function getOverviewSnapshot() {
  return overviewFixture;
}
