import { RadarPage } from "@/features/radar/components/radar-page";
import { getRadarWorkspace } from "@/features/radar/lib/get-radar-workspace";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "관심 종목 레이더",
  description: "관심 종목을 가격, 거래량, 상대강도, 섹터, 이벤트 기준으로 빠르게 좁힙니다.",
};

export default async function RadarRoute() {
  const radarWorkspace = await getRadarWorkspace();

  return <RadarPage workspace={radarWorkspace} />;
}
