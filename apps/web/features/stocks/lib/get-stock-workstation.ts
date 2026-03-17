import "server-only";

import { buildStockFixture } from "@/dev/fixtures/stock-detail";

export async function getStockWorkstation(symbol: string) {
  return buildStockFixture(symbol);
}
