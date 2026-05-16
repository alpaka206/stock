"use client";

import * as React from "react";
import {
  BadgeCheck,
  Check,
  ExternalLink,
  Headphones,
  Loader2,
  LogOut,
  Mail,
  Play,
  RefreshCw,
  Send,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ResearchPanel } from "@/components/research/research-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { layoutTokens, surfaceStyles, typographyTokens } from "@/lib/tokens";
import { cn } from "@/lib/utils";
import type {
  LocalizationJob,
  MediaAsset,
  SubscriptionPlan,
  WorkspaceData,
} from "@/features/workspace/lib/types";

type WorkspacePageProps = {
  data: WorkspaceData;
};

type ActionState = {
  busy: boolean;
  message: string;
  tone: "neutral" | "positive" | "negative";
};

const idleAction: ActionState = { busy: false, message: "", tone: "neutral" };

export function WorkspacePage({ data }: WorkspacePageProps) {
  const router = useRouter();
  const [action, setAction] = React.useState<ActionState>(idleAction);
  const [preview, setPreview] = React.useState("");
  const userId = data.auth.userId ?? "guest";
  const userEmail = data.auth.email ?? "";

  async function runAction<TPayload>(
    label: string,
    callback: () => Promise<TPayload>,
    options?: { refresh?: boolean; onSuccess?: (payload: TPayload) => void }
  ) {
    setAction({ busy: true, message: `${label} 중입니다.`, tone: "neutral" });
    try {
      const payload = await callback();
      options?.onSuccess?.(payload);
      setAction({ busy: false, message: `${label} 완료`, tone: "positive" });
      if (options?.refresh ?? true) {
        router.refresh();
      }
    } catch (error) {
      setAction({
        busy: false,
        message: error instanceof Error ? error.message : `${label} 실패`,
        tone: "negative",
      });
    }
  }

  return (
    <div className={layoutTokens.page} data-testid="workspace-page">
      <section className={cn(surfaceStyles.panel, "overflow-hidden p-[var(--card-padding)]")}>
        <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
          <div>
            <div className="flex flex-wrap gap-2">
              <WorkspacePill
                label="로그인"
                value={data.auth.authenticated ? "로그인됨" : "로그인 필요"}
                tone={data.auth.authenticated ? "positive" : "neutral"}
              />
              <WorkspacePill label="리포트" value={`${data.deliveries.length}건`} tone="neutral" />
              <WorkspacePill label="미디어 작업" value={`${data.localizationJobs.length}건`} tone="neutral" />
            </div>
            <p className={cn(typographyTokens.eyebrow, "mt-5")}>Workspace</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal lg:text-[2rem]">
              계정, 리포트, 더빙 작업을 한곳에서 관리합니다.
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
              자주 쓰는 리포트 설정과 미디어 작업 진행 상황을 서버에 저장해 어느 화면에서든
              같은 흐름으로 이어서 확인합니다.
            </p>
          </div>
          <div className="rounded-md border border-border/80 bg-muted/10 p-4">
            <p className={typographyTokens.eyebrow}>현재 사용자</p>
            <p className="mt-2 text-lg font-semibold tracking-normal">
              {data.auth.displayName ?? "로그인 전"}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {data.auth.email ?? "Google 계정 또는 이메일로 시작할 수 있습니다."}
            </p>
            {action.message ? <ActionMessage state={action} className="mt-4" /> : null}
          </div>
        </div>
      </section>

      <div className="grid gap-[var(--space-grid)] xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <AuthSection
          authenticated={data.auth.authenticated}
          userEmail={userEmail}
          googleLoginUrl={data.googleLoginUrl}
          busy={action.busy}
          runAction={runAction}
        />
        <PlanSection plans={data.plans} />
      </div>

      <ReportSection
        userId={userId}
        defaultEmail={userEmail}
        schedules={data.schedules}
        deliveries={data.deliveries}
        preview={preview}
        setPreview={setPreview}
        busy={action.busy}
        runAction={runAction}
      />

      <MediaSection
        assets={data.mediaAssets}
        jobs={data.localizationJobs}
        busy={action.busy}
        runAction={runAction}
      />
    </div>
  );
}

function AuthSection({
  authenticated,
  userEmail,
  googleLoginUrl,
  busy,
  runAction,
}: {
  authenticated: boolean;
  userEmail: string;
  googleLoginUrl: string;
  busy: boolean;
  runAction: <T>(
    label: string,
    callback: () => Promise<T>,
    options?: { refresh?: boolean; onSuccess?: (payload: T) => void }
  ) => void;
}) {
  const [email, setEmail] = React.useState(userEmail || "tester@example.com");
  const [displayName, setDisplayName] = React.useState("테스터");

  return (
    <ResearchPanel
      title="로그인"
      description="Google 계정으로 계속하거나 테스트용 이메일로 바로 시작합니다."
      action={<UserRound className="size-5 text-muted-foreground" />}
    >
      <div className="grid gap-4">
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link href={googleLoginUrl}>
              <ExternalLink className="size-4" />
              Google로 계속
            </Link>
          </Button>
          <Button
            type="button"
            variant="ghost"
            disabled={!authenticated || busy}
            onClick={() =>
              runAction("로그아웃", () =>
                requestJson("/api/auth/logout", {
                  method: "POST",
                  body: JSON.stringify({}),
                })
              )
            }
          >
            <LogOut className="size-4" />
            로그아웃
          </Button>
        </div>

        <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_180px]">
          <Input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="email@example.com"
          />
          <Input
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="표시 이름"
          />
        </div>
        <Button
          type="button"
          disabled={busy}
          onClick={() =>
            runAction("이메일 로그인", () =>
              requestJson("/api/auth/dev-login", {
                method: "POST",
                body: JSON.stringify({ email, displayName, locale: "ko" }),
              })
            )
          }
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : <Check className="size-4" />}
          이메일로 시작
        </Button>
      </div>
    </ResearchPanel>
  );
}

function PlanSection({ plans }: { plans: SubscriptionPlan[] }) {
  return (
    <ResearchPanel
      title="구독 플랜"
      description="구독 전에 각 플랜의 제공 범위를 빠르게 비교합니다."
      action={<BadgeCheck className="size-5 text-muted-foreground" />}
    >
      <div className="grid gap-3 md:grid-cols-3">
        {plans.map((plan) => (
          <PlanCard key={plan.id} plan={plan} />
        ))}
      </div>
    </ResearchPanel>
  );
}

function PlanCard({ plan }: { plan: SubscriptionPlan }) {
  const limits = parseFeatureLimits(plan.featureLimits);
  return (
    <div
      className={cn(
        "rounded-md border p-4",
        plan.code === "pro"
          ? "border-primary/45 bg-primary/10"
          : "border-border/75 bg-muted/10"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-base font-semibold tracking-normal">{plan.name}</p>
          <p className="numeric mt-1 whitespace-nowrap text-xl font-semibold">
            {Number(plan.monthlyPrice).toLocaleString("ko-KR")}
            <span className="ml-1 text-xs font-medium text-muted-foreground">{plan.currency}/월</span>
          </p>
        </div>
        {plan.code === "pro" ? <Badge className="rounded-md">추천</Badge> : null}
      </div>
      <ul className="mt-4 space-y-2 text-sm leading-6 text-muted-foreground">
        <li>관심 종목 {limits.watchlistSymbols ?? "-"}개</li>
        <li>판단 기록 {limits.savedSnapshots ?? "-"}개</li>
        <li>일간 리포트 {limits.dailyReports ? "포함" : "미포함"}</li>
        <li>주간 리포트 {limits.weeklyReports ? "포함" : "미포함"}</li>
        <li>미디어 현지화 {limits.mediaLocalizationMinutes ?? 0}분</li>
      </ul>
    </div>
  );
}

function ReportSection({
  userId,
  defaultEmail,
  schedules,
  deliveries,
  preview,
  setPreview,
  busy,
  runAction,
}: {
  userId: string;
  defaultEmail: string;
  schedules: WorkspaceData["schedules"];
  deliveries: WorkspaceData["deliveries"];
  preview: string;
  setPreview: (value: string) => void;
  busy: boolean;
  runAction: <T>(
    label: string,
    callback: () => Promise<T>,
    options?: { refresh?: boolean; onSuccess?: (payload: T) => void }
  ) => void;
}) {
  const [email, setEmail] = React.useState(defaultEmail || "research@example.com");
  const [cadence, setCadence] = React.useState<"DAILY" | "WEEKLY">("WEEKLY");
  const [symbols, setSymbols] = React.useState("NVDA, AAPL, 005930");

  const reportPayload = {
    userId,
    deliveryEmail: email,
    locale: "ko",
    cadence,
    symbols: symbols.split(",").map((symbol) => symbol.trim()).filter(Boolean),
  };

  return (
    <ResearchPanel
      title="리포트"
      description="오늘 또는 이번 주 리포트를 저장된 가격, 뉴스, 공시 기반으로 생성합니다."
      action={<Mail className="size-5 text-muted-foreground" />}
    >
      <div className="grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="grid gap-3">
          <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          <div className="grid gap-3 sm:grid-cols-[140px_1fr]">
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              value={cadence}
              onChange={(event) => setCadence(event.target.value as "DAILY" | "WEEKLY")}
            >
              <option value="DAILY">오늘</option>
              <option value="WEEKLY">이번 주</option>
            </select>
            <Input value={symbols} onChange={(event) => setSymbols(event.target.value)} />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              disabled={busy}
              onClick={() =>
                runAction(
                  "리포트 미리보기",
                  () =>
                    requestJson<{ textBody: string }>("/api/platform/reports/preview", {
                      method: "POST",
                      body: JSON.stringify(reportPayload),
                    }),
                  {
                    refresh: false,
                    onSuccess: (payload) => setPreview(payload.textBody),
                  }
                )
              }
            >
              <RefreshCw className="size-4" />
              미리보기
            </Button>
            <Button
              type="button"
              disabled={busy}
              onClick={() =>
                runAction("리포트 발송", () =>
                  requestJson("/api/platform/reports/send", {
                    method: "POST",
                    body: JSON.stringify(reportPayload),
                  })
                )
              }
            >
              <Send className="size-4" />
              이메일 발송
            </Button>
            <Button
              type="button"
              variant="ghost"
              disabled={busy}
              onClick={() =>
                runAction("리포트 예약 저장", () =>
                  requestJson("/api/platform/report-schedules", {
                    method: "POST",
                    body: JSON.stringify({
                      userId,
                      locale: "ko",
                      cadence,
                      deliveryEmail: email,
                      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                      enabled: true,
                    }),
                  })
                )
              }
            >
              예약 저장
            </Button>
          </div>
        </div>

        <div className="grid gap-3">
          {preview ? (
            <pre className="max-h-[260px] overflow-auto rounded-md border border-border/75 bg-muted/15 p-4 text-xs leading-6 text-muted-foreground">
              {preview}
            </pre>
          ) : (
            <div className="rounded-md border border-dashed border-border/70 p-4 text-sm text-muted-foreground">
              미리보기를 누르면 실제 저장 자료 기준 이메일 본문을 확인합니다.
            </div>
          )}
          <div className="grid gap-2 md:grid-cols-2">
            {schedules.slice(0, 4).map((schedule) => (
              <CompactRow
                key={schedule.id}
                title={`${schedule.cadence === "DAILY" ? "오늘" : "이번 주"} 리포트`}
                meta={`${schedule.deliveryEmail} · ${schedule.timezone}`}
                status={schedule.enabled ? "켜짐" : "꺼짐"}
              />
            ))}
            {deliveries.slice(0, 4).map((delivery) => (
              <CompactRow
                key={delivery.id}
                title={delivery.subject}
                meta={delivery.generatedAt}
                status={delivery.status}
              />
            ))}
          </div>
        </div>
      </div>
    </ResearchPanel>
  );
}

function MediaSection({
  assets,
  jobs,
  busy,
  runAction,
}: {
  assets: MediaAsset[];
  jobs: LocalizationJob[];
  busy: boolean;
  runAction: <T>(
    label: string,
    callback: () => Promise<T>,
    options?: { refresh?: boolean; onSuccess?: (payload: T) => void }
  ) => void;
}) {
  const [title, setTitle] = React.useState("Earnings call");
  const [sourceUrl, setSourceUrl] = React.useState("");
  const [kind, setKind] = React.useState<"AUDIO" | "VIDEO">("VIDEO");
  const [language, setLanguage] = React.useState("en");
  const [symbol, setSymbol] = React.useState("NVDA");
  const [selectedAssetId, setSelectedAssetId] = React.useState(assets[0]?.id ?? "");
  const [targetLanguage, setTargetLanguage] = React.useState("ko");

  React.useEffect(() => {
    if (!selectedAssetId && assets[0]?.id) {
      setSelectedAssetId(assets[0].id);
    }
  }, [assets, selectedAssetId]);

  return (
    <ResearchPanel
      title="오디오 / 영상 현지화"
      description="어닝콜, 연준 발표, 실적 영상의 더빙과 자막 작업 상태를 서버에 남깁니다."
      action={<Headphones className="size-5 text-muted-foreground" />}
    >
      <div className="grid gap-5 xl:grid-cols-[380px_minmax(0,1fr)]">
        <div className="grid gap-3">
          <div className="grid gap-3 sm:grid-cols-[120px_1fr]">
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              value={kind}
              onChange={(event) => setKind(event.target.value as "AUDIO" | "VIDEO")}
            >
              <option value="VIDEO">영상</option>
              <option value="AUDIO">오디오</option>
            </select>
            <Input value={symbol} onChange={(event) => setSymbol(event.target.value)} placeholder="티커" />
          </div>
          <Input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="자료 제목" />
          <Input value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="원본 URL" />
          <div className="grid gap-3 sm:grid-cols-2">
            <Input value={language} onChange={(event) => setLanguage(event.target.value)} placeholder="원본 언어" />
            <Input
              value={targetLanguage}
              onChange={(event) => setTargetLanguage(event.target.value)}
              placeholder="번역 언어"
            />
          </div>
          <Button
            type="button"
            disabled={busy || !sourceUrl}
            onClick={() =>
              runAction("미디어 자료 저장", () =>
                requestJson("/api/platform/media-assets", {
                  method: "POST",
                  body: JSON.stringify({
                    symbol,
                    kind,
                    title,
                    sourceUrl,
                    provider: "manual",
                    language,
                    publishedAt: new Date().toISOString(),
                  }),
                })
              )
            }
          >
            <Check className="size-4" />
            자료 저장
          </Button>
          <div className="grid gap-2">
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              value={selectedAssetId}
              onChange={(event) => setSelectedAssetId(event.target.value)}
            >
              <option value="">자료 선택</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.title}
                </option>
              ))}
            </select>
            <Button
              type="button"
              variant="outline"
              disabled={busy || !selectedAssetId}
              onClick={() =>
                runAction("현지화 작업 생성", () =>
                  requestJson("/api/platform/localization-jobs", {
                    method: "POST",
                    body: JSON.stringify({
                      mediaAssetId: selectedAssetId,
                      provider: "Perso",
                      targetLanguage,
                    }),
                  })
                )
              }
            >
              <Play className="size-4" />
              작업 생성
            </Button>
          </div>
        </div>

        <div className="grid gap-3">
          {jobs.length === 0 ? (
            <div className="rounded-md border border-dashed border-border/70 p-4 text-sm text-muted-foreground">
              저장된 현지화 작업이 없습니다. 원본 자료를 저장한 뒤 작업을 생성하세요.
            </div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="rounded-md border border-border/75 bg-muted/10 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold tracking-normal">
                      {assetTitle(assets, job.mediaAssetId)}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {job.provider} · {job.targetLanguage} · {job.providerJobId ?? "제출 전"}
                    </p>
                  </div>
                  <Badge variant="secondary" className="rounded-md">
                    {job.status}
                  </Badge>
                </div>
                {job.errorMessage ? (
                  <p className="mt-3 text-sm text-[color:var(--negative)]">{job.errorMessage}</p>
                ) : null}
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button
                    type="button"
                    size="sm"
                    disabled={busy || job.status !== "REQUESTED"}
                    onClick={() =>
                      runAction("Perso 제출", () =>
                        requestJson(`/api/platform/localization-jobs/${job.id}/submit`, {
                          method: "POST",
                          body: JSON.stringify({
                            sourceLanguageCode: "auto",
                            withLipSync: false,
                            numberOfSpeakers: 1,
                            preferredSpeedType: "GREEN",
                          }),
                        })
                      )
                    }
                  >
                    제출
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={busy || !job.providerJobId}
                    onClick={() =>
                      runAction("Perso 상태 동기화", () =>
                        requestJson(`/api/platform/localization-jobs/${job.id}/sync`, {
                          method: "POST",
                          body: JSON.stringify({}),
                        })
                      )
                    }
                  >
                    <RefreshCw className="size-4" />
                    동기화
                  </Button>
                  {job.dubbedAudioUrl ? (
                    <Button asChild size="sm" variant="ghost">
                      <Link href={job.dubbedAudioUrl}>오디오</Link>
                    </Button>
                  ) : null}
                  {job.subtitleUrl ? (
                    <Button asChild size="sm" variant="ghost">
                      <Link href={job.subtitleUrl}>자막</Link>
                    </Button>
                  ) : null}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </ResearchPanel>
  );
}

function WorkspacePill({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "positive" | "neutral";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-md border px-3 py-2 text-xs",
        tone === "positive"
          ? "border-[color:color-mix(in_oklch,var(--positive)_28%,transparent)] bg-[color:color-mix(in_oklch,var(--positive)_10%,transparent)] text-foreground"
          : "border-border/80 bg-muted/15 text-muted-foreground"
      )}
    >
      <span>{label}</span>
      <span className="font-semibold text-foreground">{value}</span>
    </span>
  );
}

function CompactRow({ title, meta, status }: { title: string; meta: string; status: string }) {
  return (
    <div className="rounded-md border border-border/75 bg-muted/10 p-3">
      <div className="flex items-start justify-between gap-3">
        <p className="line-clamp-2 text-sm font-medium">{title}</p>
        <span className="rounded-md bg-muted px-2 py-1 text-[0.68rem] text-muted-foreground">
          {status}
        </span>
      </div>
      <p className="numeric mt-2 truncate text-xs text-muted-foreground">{meta}</p>
    </div>
  );
}

function ActionMessage({ state, className }: { state: ActionState; className?: string }) {
  return (
    <p
      className={cn(
        "rounded-md border px-3 py-2 text-sm",
        state.tone === "positive"
          ? "border-[color:color-mix(in_oklch,var(--positive)_28%,transparent)] text-[color:var(--positive)]"
          : state.tone === "negative"
            ? "border-[color:color-mix(in_oklch,var(--negative)_28%,transparent)] text-[color:var(--negative)]"
            : "border-border/75 text-muted-foreground",
        className
      )}
    >
      {state.message}
    </p>
  );
}

async function requestJson<TPayload = unknown>(url: string, init: RequestInit): Promise<TPayload> {
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...init.headers,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      typeof payload?.message === "string" ? payload.message : `요청이 실패했습니다. (${response.status})`
    );
  }
  return payload as TPayload;
}

function parseFeatureLimits(value: string) {
  try {
    return JSON.parse(value) as Record<string, number | boolean>;
  } catch {
    return {};
  }
}

function assetTitle(assets: MediaAsset[], assetId: string) {
  return assets.find((asset) => asset.id === assetId)?.title ?? "미디어 자료";
}
