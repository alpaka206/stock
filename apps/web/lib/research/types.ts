export type TrendDirection = "up" | "down" | "flat";
export type Tone = "positive" | "negative" | "neutral";

export type SavedViewPreset<TValue> = {
  id: string;
  name: string;
  value: TValue;
  updatedAt: string;
};

export type AvailabilityState = {
  label: string;
  reason: string;
  expectedSource?: string;
};

export type InstrumentCatalogItem = {
  symbol: string;
  name: string;
  securityCode: string;
  aliases: string[];
  sector?: string;
  exchange?: string;
};

export type IndexStripItem = {
  name: string;
  symbol: string;
  category: string;
  value: number;
  changePercent: number;
  note: string;
  href: string;
};

export type NewsItem = {
  id: string;
  source: string;
  headline: string;
  summary: string;
  publishedAt: string;
  impactLabel: string;
  tone: Tone;
  href?: string;
  sector?: string;
  sourceRefIds?: string[];
};

export type SectorStrengthItem = {
  id: string;
  name: string;
  score: number;
  changePercent?: number;
  direction: TrendDirection;
  momentum: string;
  catalysts: string[];
  targetSymbol: string;
  href: string;
};

export type RiskBannerItem = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
  href: string;
};

export type OverviewDriverItem = {
  label: string;
  text: string;
  tone: Tone;
  href: string;
};

export type HeatmapTile = {
  label: string;
  score: number;
  changePercent?: number;
  href: string;
};

export type OverviewConfidence = {
  score: number;
  label: "low" | "medium" | "high";
  rationale: string;
};

export type OverviewSourceSummary = {
  sourceCount: number;
  missingDataCount: number;
};

export type OverviewFixture = {
  asOf: string;
  lead: string;
  scenario: string;
  summaryDrivers: OverviewDriverItem[];
  indices: IndexStripItem[];
  news: NewsItem[];
  sectors: SectorStrengthItem[];
  risks: RiskBannerItem[];
  heatmap: HeatmapTile[];
  confidence: OverviewConfidence;
  sourceSummary: OverviewSourceSummary;
};

export type WatchlistFolderNode = {
  id: string;
  label: string;
  count: number;
  description: string;
  tags?: string[];
  children?: WatchlistFolderNode[];
};

export type RadarColumnKey =
  | "symbol"
  | "name"
  | "securityCode"
  | "price"
  | "changePercent"
  | "score"
  | "volumeRatio"
  | "relativeStrength"
  | "sector"
  | "nextEvent"
  | "thesis";

export type RadarViewMode = "core" | "volume" | "risk";
export type RadarGroupMode = "flat" | "sector";

export type RadarSortItem = {
  colId: RadarColumnKey;
  sort: "asc" | "desc";
};

export type RadarViewPresetState = {
  folderId: string;
  query: string;
  viewMode: RadarViewMode;
  groupMode: RadarGroupMode;
  sector: string;
  selectedSymbol: string;
  visibleColumns: RadarColumnKey[];
  sortModel: RadarSortItem[];
};

export type WatchlistRow = {
  symbol: string;
  name: string;
  securityCode: string;
  sector: string;
  folderId: string;
  tags: string[];
  price: number;
  changePercent: number;
  volumeRatio: number;
  relativeStrength: number;
  score: number;
  nextEvent: string;
  thesis: string;
  condition: string;
  sourceRefIds?: string[];
};

export type SectorInsightCard = {
  sector: string;
  score: number;
  thesis: string;
  catalyst: string;
  topPick: string;
  sourceRefIds?: string[];
};

export type ScheduleItem = {
  sector?: string;
  time: string;
  title: string;
  note: string;
  sourceRefIds?: string[];
};

export type BrokerReportItem = {
  sector?: string;
  house: string;
  symbol: string;
  stance: string;
  summary: string;
  sourceRefIds?: string[];
};

export type TopPickItem = {
  sector?: string;
  symbol: string;
  reason: string;
  score: number;
  sourceRefIds?: string[];
};

export type RadarFixture = {
  folders: WatchlistFolderNode[];
  rows: WatchlistRow[];
  sectorCards: SectorInsightCard[];
  schedules: ScheduleItem[];
  issues: NewsItem[];
  reports: BrokerReportItem[];
  topPicks: TopPickItem[];
  defaultVisibleColumns: RadarColumnKey[];
  defaultViewMode: RadarViewMode;
  defaultGroupMode: RadarGroupMode;
  defaultSelectedFolderId: string;
  savedViews: SavedViewPreset<RadarViewPresetState>[];
};

export type PricePoint = {
  label: string;
  close: number;
  volume: number;
  date?: string;
};

export type ChartGuide = {
  id: string;
  label: string;
  value: number;
  tone: Tone;
  description?: string;
  enabled?: boolean;
};

export type ChartMarker = {
  id: string;
  label: string;
  tone: Tone;
  date?: string;
  pointLabel?: string;
  title?: string;
  detail?: string;
  href?: string;
};

export type IndicatorRuleDefinition = {
  id: string;
  label: string;
  description: string;
  enabledByDefault: boolean;
  tone?: Tone;
};

export type ScoreBreakdownItem = {
  label: string;
  score: number;
  summary: string;
};

export type FlowItem = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
};

export type ShortOptionMetric = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
};

export type StockIssueItem = {
  title: string;
  source: string;
  summary: string;
  tone: Tone;
  category?: string;
  href?: string;
};

export type StockInstrument = {
  symbol: string;
  name: string;
  exchange: string;
  securityCode: string;
  sector: string;
  marketCap: string;
};

export type StockScoreSummary = {
  total: number;
  confidence: OverviewConfidence;
  breakdown: ScoreBreakdownItem[];
};

export type StockRulePresetState = {
  presetId: string;
  indicatorIds: string[];
};

export type StockFixture = {
  instrument: StockInstrument;
  price: number;
  changePercent: number;
  thesis: string;
  priceSeries: PricePoint[];
  eventMarkers: ChartMarker[];
  indicatorGuides: ChartGuide[];
  rulePresetDefinitions: IndicatorRuleDefinition[];
  scoreSummary: StockScoreSummary;
  flowMetrics: FlowItem[];
  flowUnavailable?: AvailabilityState;
  optionsShortMetrics: ShortOptionMetric[];
  optionsUnavailable?: AvailabilityState;
  issues: StockIssueItem[];
  relatedSymbols: string[];
};

export type HistoryRangeOption = {
  value: string;
  label: string;
};

export type HistoryEvent = {
  id: string;
  date: string;
  title: string;
  category: string;
  summary: string;
  reaction: string;
  tone: Tone;
  source?: string;
  url?: string;
  sourceRefIds?: string[];
};

export type MoveReason = {
  label: string;
  description: string;
  tone: Tone;
  relatedDate?: string;
};

export type OverlapIndicator = {
  label: string;
  detail: string;
  tone: Tone;
  relatedDate?: string;
};

export type HistoryFixture = {
  symbol: string;
  range: string;
  availableRanges: HistoryRangeOption[];
  priceSeries: PricePoint[];
  eventMarkers: ChartMarker[];
  events: HistoryEvent[];
  moveSummary: string;
  moveReasons: MoveReason[];
  overlaps: OverlapIndicator[];
};
