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
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  headerClassName?: string;
  size?: "default" | "sm";
  variant?: "default" | "brief" | "feed" | "risk";
};

export function ResearchPanel({
  eyebrow,
  title,
  description,
  action,
  children,
  className,
  contentClassName,
  headerClassName,
  size = "default",
  variant = "default",
}: ResearchPanelProps) {
  const variantClassName =
    variant === "brief"
      ? "bg-[linear-gradient(180deg,color-mix(in_oklch,var(--primary)_5%,var(--card)),var(--card))]"
      : variant === "risk"
        ? "border-[color:color-mix(in_oklch,var(--negative)_24%,var(--border))]"
        : "";

  return (
    <Card
      size={size}
      className={cn(surfaceStyles.panel, variantClassName, className)}
    >
      <CardHeader
        className={cn("gap-2 border-b border-border/80 pb-4", headerClassName)}
      >
        <div>
          {eyebrow ? (
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground/85">
              {eyebrow}
            </p>
          ) : null}
          <CardTitle className={cn(eyebrow ? "mt-1.5" : undefined)}>
            {title}
          </CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {action ? <CardAction>{action}</CardAction> : null}
      </CardHeader>
      <CardContent
        className={cn("p-[var(--card-padding)] pt-[var(--card-padding)]", contentClassName)}
      >
        {children}
      </CardContent>
    </Card>
  );
}
