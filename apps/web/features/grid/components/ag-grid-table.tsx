"use client";

import type { ColDef, GridOptions, RowClickedEvent } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";

import {
  agGridLocaleText,
  createDefaultColDef,
  ensureAgGridModules,
} from "@/features/grid/lib/ag-grid-config";
import { cn } from "@/lib/utils";

ensureAgGridModules();

type AgGridTableProps<TData extends object> = {
  rowData: TData[];
  columnDefs: ColDef<TData>[];
  className?: string;
  emptyMessage?: string;
  defaultColDef?: ColDef<TData>;
  gridOptions?: GridOptions<TData>;
  onRowClicked?: (event: RowClickedEvent<TData>) => void;
};

export function AgGridTable<TData extends object>({
  rowData,
  columnDefs,
  className,
  emptyMessage = "표시할 데이터가 없습니다.",
  defaultColDef,
  gridOptions,
  onRowClicked,
}: AgGridTableProps<TData>) {
  if (rowData.length === 0) {
    return (
      <div
        className={cn(
          "flex h-[440px] items-center justify-center rounded-[calc(var(--radius)*1.3)] border border-dashed border-border/70 bg-background/35 text-sm text-muted-foreground",
          className
        )}
      >
        {emptyMessage}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "ag-theme-quartz h-[440px] overflow-hidden rounded-[calc(var(--radius)*1.3)]",
        className
      )}
    >
      <AgGridReact<TData>
        rowData={rowData}
        columnDefs={columnDefs}
        localeText={agGridLocaleText}
        defaultColDef={defaultColDef ?? createDefaultColDef<TData>()}
        theme="legacy"
        animateRows
        onRowClicked={onRowClicked}
        rowHeight={42}
        headerHeight={42}
        gridOptions={gridOptions}
      />
    </div>
  );
}
