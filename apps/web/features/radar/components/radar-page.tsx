import type { RadarFixture } from "@/lib/research/types";

import { RadarWorkbench } from "@/features/radar/components/radar-workbench";

export function RadarPage({ workspace }: { workspace: RadarFixture }) {
  return <RadarWorkbench workspace={workspace} />;
}
