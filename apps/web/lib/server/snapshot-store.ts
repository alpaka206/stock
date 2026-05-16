import "server-only";

import { randomUUID } from "node:crypto";

import type { ResearchSnapshot } from "@/lib/research/types";

const MAX_RESEARCH_SNAPSHOTS = 120;

let memorySnapshots: ResearchSnapshot[] = [];

export async function listServerSnapshots(symbol?: string | null) {
  const normalizedSymbol = symbol?.trim().toUpperCase();

  return memorySnapshots
    .filter((snapshot) =>
      normalizedSymbol ? snapshot.symbol.toUpperCase() === normalizedSymbol : true
    )
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt));
}

export async function saveServerSnapshot(
  input: Partial<ResearchSnapshot> & Omit<ResearchSnapshot, "id" | "createdAt">
) {
  const snapshot: ResearchSnapshot = {
    ...input,
    id: input.id || randomUUID(),
    createdAt: input.createdAt || new Date().toISOString(),
    symbol: input.symbol.trim().toUpperCase(),
    name: input.name.trim(),
    exchange: input.exchange.trim(),
    securityCode: input.securityCode.trim(),
    sector: input.sector.trim(),
    note: input.note.trim(),
  };

  memorySnapshots = [
    snapshot,
    ...memorySnapshots.filter((item) => item.id !== snapshot.id),
  ].slice(0, MAX_RESEARCH_SNAPSHOTS);

  return snapshot;
}

export async function deleteServerSnapshot(id: string) {
  const nextSnapshots = memorySnapshots.filter((snapshot) => snapshot.id !== id);
  const deleted = nextSnapshots.length !== memorySnapshots.length;
  memorySnapshots = nextSnapshots;
  return deleted;
}
