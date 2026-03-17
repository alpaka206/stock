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

  const isDark = resolvedTheme === "dark";

  return (
    <Button
      variant="outline"
      size="icon-sm"
      type="button"
      onClick={() => mounted && setTheme(isDark ? "light" : "dark")}
      aria-label={isDark ? "라이트모드로 전환" : "다크모드로 전환"}
    >
      {mounted && isDark ? <SunMedium /> : <MoonStar />}
    </Button>
  );
}
