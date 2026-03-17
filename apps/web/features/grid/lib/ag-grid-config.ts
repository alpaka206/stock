import { AG_GRID_LOCALE_KR } from "@ag-grid-community/locale";
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
} from "ag-grid-community";

declare global {
  var __stockWorkspaceAgGridRegistered__: boolean | undefined;
}

const globalScope = globalThis as typeof globalThis & {
  __stockWorkspaceAgGridRegistered__?: boolean;
};

export function ensureAgGridModules() {
  if (!globalScope.__stockWorkspaceAgGridRegistered__) {
    ModuleRegistry.registerModules([AllCommunityModule]);
    globalScope.__stockWorkspaceAgGridRegistered__ = true;
  }
}

export const agGridLocaleText = AG_GRID_LOCALE_KR;

export function createDefaultColDef<TData>(): ColDef<TData> {
  return {
    sortable: true,
    resizable: true,
    filter: true,
    minWidth: 108,
    suppressHeaderMenuButton: true,
  };
}
