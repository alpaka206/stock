import { RadarPage } from "@/features/radar/components/radar-page";
import { getRadarWorkspace } from "@/features/radar/lib/get-radar-workspace";

export default async function RadarRoute() {
  const radarWorkspace = await getRadarWorkspace();

  return <RadarPage workspace={radarWorkspace} />;
}
