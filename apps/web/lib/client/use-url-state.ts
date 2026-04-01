"use client";

import * as React from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

type UrlUpdateValue = string | null | undefined;

export function useUrlState() {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();

  const replaceParams = React.useCallback(
    (updates: Record<string, UrlUpdateValue>) => {
      const nextParams = new URLSearchParams(searchParams.toString());

      Object.entries(updates).forEach(([key, value]) => {
        if (value === undefined || value === null || value === "") {
          nextParams.delete(key);
          return;
        }

        nextParams.set(key, value);
      });

      const nextQuery = nextParams.toString();
      const nextHref = nextQuery ? `${pathname}?${nextQuery}` : pathname;
      router.replace(nextHref, { scroll: false });
    },
    [pathname, router, searchParams]
  );

  return {
    pathname,
    searchParams,
    replaceParams,
  };
}

export function useQueryValue(key: string, fallback = "") {
  const searchParams = useSearchParams();
  return searchParams.get(key) ?? fallback;
}

export function useDebouncedValue<TValue>(value: TValue, delayMs = 180) {
  const [debouncedValue, setDebouncedValue] = React.useState(value);

  React.useEffect(() => {
    const handle = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delayMs);

    return () => window.clearTimeout(handle);
  }, [delayMs, value]);

  return debouncedValue;
}
