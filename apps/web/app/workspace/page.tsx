import { WorkspacePage } from "@/features/workspace/components/workspace-page";
import { getWorkspaceData } from "@/features/workspace/lib/get-workspace-data";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "워크스페이스",
  description: "계정, 구독 플랜, 리포트 이메일, 미디어 더빙 작업을 관리합니다.",
};

export default async function WorkspaceRoute() {
  const data = await getWorkspaceData();

  return <WorkspacePage data={data} />;
}
