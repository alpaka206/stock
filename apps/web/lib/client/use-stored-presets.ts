"use client";

import type { SavedViewPreset } from "@/lib/research/types";
import { useStoredState } from "@/lib/client/use-stored-state";

export function useStoredPresets<TValue>(
  storageKey: string,
  initialValue: SavedViewPreset<TValue>[]
) {
  const { hasLoaded, value: presets, setValue: setPresets } = useStoredState(
    storageKey,
    initialValue
  );

  function savePreset(name: string, value: TValue) {
    const nextPreset: SavedViewPreset<TValue> = {
      id: `${Date.now()}`,
      name,
      value,
      updatedAt: new Date().toISOString(),
    };

    setPresets((currentPresets) => [nextPreset, ...currentPresets] as typeof presets);
  }

  function removePreset(presetId: string) {
    setPresets((currentPresets) =>
      currentPresets.filter((preset) => preset.id !== presetId)
    );
  }

  return {
    hasLoaded,
    presets,
    savePreset,
    removePreset,
  };
}
