"use client";

import * as React from "react";
import { MoonStar, SunMedium } from "lucide-react";
import { useTheme } from "next-themes";

import { useAppLanguage } from "@/components/providers/language-provider";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const { messages } = useAppLanguage();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted ? resolvedTheme === "dark" : true;
  const ariaLabel = mounted
    ? isDark
      ? messages.theme.toLight
      : messages.theme.toDark
    : messages.theme.pending;

  return (
    <Button
      variant="outline"
      size="icon-sm"
      type="button"
      disabled={!mounted}
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label={ariaLabel}
    >
      {mounted && isDark ? <SunMedium /> : <MoonStar />}
    </Button>
  );
}
