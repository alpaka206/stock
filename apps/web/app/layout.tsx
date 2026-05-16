import type { Metadata } from "next";

import { AppProviders } from "@/components/providers/app-providers";
import { AppShell } from "@/components/shell/app-shell";

import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Stock Desk",
    template: "%s | Stock Desk",
  },
  description:
    "미국장과 국내장을 함께 읽는 주식 리서치 워크스페이스. 시장 흐름, 종목 차트, 뉴스, 공시, 이벤트, 판단 기록을 한곳에서 확인합니다.",
  applicationName: "Stock Desk",
  keywords: [
    "주식",
    "미국 주식",
    "한국 주식",
    "종목 분석",
    "공시",
    "뉴스",
    "실적 발표",
  ],
  alternates: {
    canonical: "/overview",
    languages: {
      ko: "/overview",
      en: "/overview?lang=en",
      ja: "/overview?lang=ja",
      zh: "/overview?lang=zh",
    },
  },
  openGraph: {
    type: "website",
    title: "Stock Desk",
    description:
      "시장 흐름, 종목 차트, 뉴스, 공시, 이벤트, 판단 기록을 한곳에서 확인합니다.",
    url: "/overview",
    siteName: "Stock Desk",
    locale: "ko_KR",
  },
  twitter: {
    card: "summary",
    title: "Stock Desk",
    description: "미국장과 국내장을 함께 읽는 주식 리서치 워크스페이스",
  },
  icons: {
    icon: "/icon.svg",
    apple: "/apple-icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <AppProviders>
          <AppShell>{children}</AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
