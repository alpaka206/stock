"use client";

import * as React from "react";

export function useStoredState<TValue>(
  storageKey: string,
  initialValue: TValue
) {
  const [value, setValue] = React.useState(initialValue);
  const [hasLoaded, setHasLoaded] = React.useState(false);
  const initialValueRef = React.useRef(initialValue);

  React.useEffect(() => {
    initialValueRef.current = initialValue;
  }, [initialValue]);

  React.useEffect(() => {
    try {
      const rawValue = window.localStorage.getItem(storageKey);

      if (rawValue) {
        setValue(JSON.parse(rawValue) as TValue);
      } else {
        setValue(initialValueRef.current);
      }
    } catch {
      setValue(initialValueRef.current);
    } finally {
      setHasLoaded(true);
    }
  }, [storageKey]);

  React.useEffect(() => {
    if (!hasLoaded) {
      return;
    }

    window.localStorage.setItem(storageKey, JSON.stringify(value));
  }, [hasLoaded, storageKey, value]);

  return {
    hasLoaded,
    value,
    setValue,
  };
}
