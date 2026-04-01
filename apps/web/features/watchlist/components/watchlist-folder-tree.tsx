"use client";

import type { WatchlistFolderNode } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type WatchlistFolderTreeProps = {
  folders: WatchlistFolderNode[];
  activeId: string;
  onSelect: (folderId: string) => void;
};

export function WatchlistFolderTree({
  folders,
  activeId,
  onSelect,
}: WatchlistFolderTreeProps) {
  return (
    <div className="space-y-2">
      {folders.map((folder) => (
        <FolderNode
          key={folder.id}
          node={folder}
          depth={0}
          activeId={activeId}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

function FolderNode({
  node,
  depth,
  activeId,
  onSelect,
}: {
  node: WatchlistFolderNode;
  depth: number;
  activeId: string;
  onSelect: (folderId: string) => void;
}) {
  const active = activeId === node.id;

  return (
    <div className="space-y-2">
      <button
        type="button"
        onClick={() => onSelect(node.id)}
        className={cn(
          "flex w-full items-start justify-between rounded-[calc(var(--radius)*1.05)] border px-3 py-2 text-left transition-colors",
          active
            ? "border-primary/35 bg-primary/10"
            : "border-border/60 bg-background/25 hover:bg-muted/65"
        )}
        style={{ paddingLeft: `${depth * 14 + 12}px` }}
      >
        <div className="min-w-0">
          <p className="text-sm font-semibold tracking-tight">{node.label}</p>
          <p className="mt-1 text-xs leading-5 text-muted-foreground">
            {node.description}
          </p>
        </div>
        <span className="numeric rounded-full bg-muted px-2 py-1 text-xs">
          {node.count}
        </span>
      </button>

      {node.children ? (
        <div className="space-y-2 border-l border-border/50 pl-2">
          {node.children.map((childNode) => (
            <FolderNode
              key={childNode.id}
              node={childNode}
              depth={depth + 1}
              activeId={activeId}
              onSelect={onSelect}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
