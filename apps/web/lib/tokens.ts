export const layoutTokens = {
  page:
    "mx-auto flex w-full max-w-[1760px] flex-col gap-[var(--space-section)] px-[var(--space-page)] py-[var(--space-page)] lg:px-[var(--space-page-lg)] lg:py-[var(--space-page-lg)]",
  heroGrid: "grid gap-[var(--space-grid)] xl:grid-cols-[1.08fr_0.92fr]",
  threePanelGrid:
    "grid gap-[var(--space-grid)] xl:grid-cols-[280px_minmax(0,1fr)_340px]",
  splitPanelGrid: "grid gap-[var(--space-grid)] xl:grid-cols-[1.3fr_0.7fr]",
  denseGrid: "grid gap-[var(--space-grid)] md:grid-cols-2 xl:grid-cols-4",
} as const;

export const surfaceStyles = {
  panel:
    "panel-surface rounded-[calc(var(--radius)*1.05)] border border-border/80",
  panelInset:
    "rounded-[calc(var(--radius)*0.78)] border border-border/75 bg-muted/20",
  strip:
    "rounded-[calc(var(--radius)*0.95)] border border-border/80 bg-card/88",
} as const;

export const typographyTokens = {
  eyebrow:
    "text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground/85",
  title: "text-lg font-semibold tracking-tight text-foreground lg:text-[1.4rem]",
  body: "text-sm leading-6 text-muted-foreground",
  numeric: "numeric text-[0.95em]",
} as const;
