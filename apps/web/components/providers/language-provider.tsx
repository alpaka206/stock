"use client";

import * as React from "react";

import { useStoredState } from "@/lib/client/use-stored-state";
import type { AppLanguage } from "@/lib/i18n/messages";
import { getMessages } from "@/lib/i18n/messages";

type LanguageContextValue = {
  language: AppLanguage;
  setLanguage: (language: AppLanguage) => void;
  messages: ReturnType<typeof getMessages>;
};

const LANGUAGE_STORAGE_KEY = "stock-workspace:language";

const LanguageContext = React.createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const { value, setValue } = useStoredState<AppLanguage>(LANGUAGE_STORAGE_KEY, "ko");

  const contextValue = React.useMemo<LanguageContextValue>(
    () => ({
      language: value,
      setLanguage: setValue,
      messages: getMessages(value),
    }),
    [setValue, value]
  );

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useAppLanguage() {
  const context = React.useContext(LanguageContext);

  if (!context) {
    throw new Error("useAppLanguage must be used within LanguageProvider");
  }

  return context;
}
