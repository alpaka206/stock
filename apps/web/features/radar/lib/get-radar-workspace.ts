import "server-only";

import { radarFixture } from "@/dev/fixtures/radar";

export async function getRadarWorkspace() {
  return radarFixture;
}
