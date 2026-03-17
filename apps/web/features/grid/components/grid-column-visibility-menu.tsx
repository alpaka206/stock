"use client";

import { Columns3 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export type GridColumnOption = {
  key: string;
  label: string;
  checked: boolean;
  disabled?: boolean;
};

type GridColumnVisibilityMenuProps = {
  options: GridColumnOption[];
  onCheckedChange: (key: string, checked: boolean) => void;
};

export function GridColumnVisibilityMenu({
  options,
  onCheckedChange,
}: GridColumnVisibilityMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" type="button">
          <Columns3 />
          컬럼
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>표시 컬럼</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {options.map((option) => (
          <DropdownMenuCheckboxItem
            key={option.key}
            checked={option.checked}
            disabled={option.disabled}
            onCheckedChange={(checked) =>
              onCheckedChange(option.key, checked === true)
            }
          >
            {option.label}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
