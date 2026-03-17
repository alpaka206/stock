import type { ReactNode } from "react";

import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { surfaceStyles } from "@/lib/tokens";
import { cn } from "@/lib/utils";

type ResearchPanelProps = {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  size?: "default" | "sm";
};

export function ResearchPanel({
  title,
  description,
  action,
  children,
  className,
  contentClassName,
  size = "default",
}: ResearchPanelProps) {
  return (
    <Card size={size} className={cn(surfaceStyles.panel, className)}>
      <CardHeader className="gap-2 border-b border-border/50 pb-4">
        <div>
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {action ? <CardAction>{action}</CardAction> : null}
      </CardHeader>
      <CardContent className={cn("p-[var(--card-padding)]", contentClassName)}>
        {children}
      </CardContent>
    </Card>
  );
}
