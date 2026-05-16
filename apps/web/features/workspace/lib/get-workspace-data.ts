import "server-only";

import { headers } from "next/headers";

import { buildBackendUrl, getBackendBaseUrl } from "@/lib/server/backend-url";
import type {
  LocalizationJob,
  MediaAsset,
  ReportDelivery,
  ReportSchedule,
  SubscriptionPlan,
  UserSession,
  WorkspaceData,
} from "@/features/workspace/lib/types";

const anonymousSession: UserSession = {
  authenticated: false,
  userId: null,
  email: null,
  displayName: null,
  locale: null,
  role: null,
  accessTokenExpiresAt: null,
  refreshTokenExpiresAt: null,
};

export async function getWorkspaceData(): Promise<WorkspaceData> {
  const requestHeaders = await headers();
  const cookieHeader = requestHeaders.get("cookie") ?? "";
  const auth = await fetchBackend<UserSession>("/auth/me", cookieHeader, anonymousSession);
  const userId = auth.userId ?? "guest";
  const [plansPayload, schedulesPayload, deliveriesPayload, mediaPayload, jobsPayload] =
    await Promise.all([
      fetchBackend<{ plans: SubscriptionPlan[] }>("/subscription-plans", cookieHeader, { plans: [] }),
      fetchBackend<{ schedules: ReportSchedule[] }>(
        `/report-schedules?userId=${encodeURIComponent(userId)}`,
        cookieHeader,
        { schedules: [] }
      ),
      fetchBackend<{ deliveries: ReportDelivery[] }>(
        `/reports?userId=${encodeURIComponent(userId)}`,
        cookieHeader,
        { deliveries: [] }
      ),
      fetchBackend<{ assets: MediaAsset[] }>("/media-assets", cookieHeader, { assets: [] }),
      fetchBackend<{ jobs: LocalizationJob[] }>("/localization-jobs", cookieHeader, { jobs: [] }),
    ]);

  return {
    auth,
    plans: plansPayload.plans,
    schedules: schedulesPayload.schedules,
    deliveries: deliveriesPayload.deliveries,
    mediaAssets: mediaPayload.assets,
    localizationJobs: jobsPayload.jobs,
    googleLoginUrl: `${getBackendBaseUrl()}/oauth2/authorization/google`,
  };
}

async function fetchBackend<TPayload>(
  path: string,
  cookieHeader: string,
  fallback: TPayload
) {
  try {
    const response = await fetch(buildBackendUrl(path), {
      cache: "no-store",
      headers: {
        Accept: "application/json",
        Cookie: cookieHeader,
      },
    });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as TPayload;
  } catch {
    return fallback;
  }
}
