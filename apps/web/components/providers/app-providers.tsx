"use client";

import * as React from "react";

import { LanguageProvider } from "@/components/providers/language-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeProvider } from "@/components/providers/theme-provider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <QueryProvider>{children}</QueryProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
