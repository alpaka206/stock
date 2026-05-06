"use client";

import * as React from "react";

import { useAppLanguage } from "@/components/providers/language-provider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { appLanguageOptions, type AppLanguage } from "@/lib/i18n/messages";

export function LanguageSelect() {
  const { language, setLanguage, messages } = useAppLanguage();

  return (
    <Select value={language} onValueChange={(value) => setLanguage(value as AppLanguage)}>
      <SelectTrigger className="w-[132px] bg-background/75">
        <SelectValue placeholder={messages.topbar.languagePlaceholder} />
      </SelectTrigger>
      <SelectContent>
        {appLanguageOptions.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
