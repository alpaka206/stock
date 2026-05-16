export type UserSession = {
  authenticated: boolean;
  userId: string | null;
  email: string | null;
  displayName: string | null;
  locale: string | null;
  role: string | null;
  accessTokenExpiresAt: string | null;
  refreshTokenExpiresAt: string | null;
};

export type SubscriptionPlan = {
  id: string;
  code: string;
  name: string;
  monthlyPrice: number;
  currency: string;
  featureLimits: string;
  active: boolean;
};

export type ReportSchedule = {
  id: string;
  userId: string;
  locale: string;
  cadence: "DAILY" | "WEEKLY";
  deliveryEmail: string;
  timezone: string;
  enabled: boolean;
  createdAt: string;
};

export type ReportDelivery = {
  id: string;
  userId: string;
  deliveryEmail: string;
  locale: string;
  cadence: "DAILY" | "WEEKLY";
  subject: string;
  status: "READY" | "SENT" | "FAILED";
  errorMessage: string | null;
  generatedAt: string;
  sentAt: string | null;
};

export type MediaAsset = {
  id: string;
  symbol: string;
  materialId: string | null;
  kind: "AUDIO" | "VIDEO";
  title: string;
  sourceUrl: string;
  provider: string;
  language: string;
  publishedAt: string | null;
  createdAt: string;
};

export type LocalizationJob = {
  id: string;
  mediaAssetId: string;
  provider: string;
  providerJobId: string | null;
  targetLanguage: string;
  status: "REQUESTED" | "PROCESSING" | "COMPLETED" | "FAILED";
  dubbedAudioUrl: string | null;
  subtitleUrl: string | null;
  errorMessage: string | null;
  requestedAt: string;
  completedAt: string | null;
};

export type WorkspaceData = {
  auth: UserSession;
  plans: SubscriptionPlan[];
  schedules: ReportSchedule[];
  deliveries: ReportDelivery[];
  mediaAssets: MediaAsset[];
  localizationJobs: LocalizationJob[];
  googleLoginUrl: string;
};
