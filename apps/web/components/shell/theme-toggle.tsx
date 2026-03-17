"use client";

import * as React from "react";
import { MoonStar, SunMedium } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted ? resolvedTheme === "dark" : true;
  const ariaLabel = mounted
    ? isDark
      ? "라이트 모드로 전환"
      : "다크 모드로 전환"
    : "테마 전환";

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
