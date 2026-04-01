import { Suspense } from "react";

import type { RadarFixture } from "@/lib/research/types";

import { RadarWorkbench } from "@/features/radar/components/radar-workbench";

export function RadarPage({ workspace }: { workspace: RadarFixture }) {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">레이더 화면을 준비하는 중입니다.</div>}>
      <RadarWorkbench workspace={workspace} />
    </Suspense>
  );
}
