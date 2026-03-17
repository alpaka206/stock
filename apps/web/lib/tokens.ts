export const layoutTokens = {
  page:
    "mx-auto flex w-full max-w-[1600px] flex-col gap-[var(--space-section)] px-[var(--space-page)] py-[var(--space-page)] lg:px-[var(--space-page-lg)] lg:py-[var(--space-page-lg)]",
  heroGrid: "grid gap-[var(--space-grid)] xl:grid-cols-[1.1fr_0.9fr]",
  threePanelGrid:
    "grid gap-[var(--space-grid)] xl:grid-cols-[280px_minmax(0,1fr)_340px]",
  splitPanelGrid: "grid gap-[var(--space-grid)] xl:grid-cols-[1.3fr_0.7fr]",
  denseGrid: "grid gap-[var(--space-grid)] md:grid-cols-2 xl:grid-cols-4]",
} as const;

export const surfaceStyles = {
  panel:
    "panel-surface rounded-[calc(var(--radius)*1.4)] border border-border/60 backdrop-blur-xl",
  panelInset:
    "rounded-[calc(var(--radius)*1.1)] border border-border/50 bg-background/35",
} as const;

export const typographyTokens = {
  eyebrow:
    "text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground",
  title: "text-xl font-semibold tracking-tight text-foreground lg:text-2xl",
  body: "text-sm leading-6 text-muted-foreground",
  numeric: "numeric text-[0.95em]",
} as const;
