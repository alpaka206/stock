import type { Metadata } from "next";

import { AppProviders } from "@/components/providers/app-providers";
import { AppShell } from "@/components/shell/app-shell";

import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Research Workspace",
  description: "뉴스, 차트, 섹터, 수급, 점수를 한 흐름으로 보는 금융 리서치 워크스페이스",
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
