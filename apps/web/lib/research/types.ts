export type TrendDirection = "up" | "down" | "flat";
export type Tone = "positive" | "negative" | "neutral";

export type IndexStripItem = {
  name: string;
  symbol: string;
  value: number;
  changePercent: number;
  note: string;
};

export type NewsItem = {
  id: string;
  source: string;
  headline: string;
  summary: string;
  publishedAt: string;
  impactLabel: string;
  tone: Tone;
};

export type SectorStrengthItem = {
  id: string;
  name: string;
  score: number;
  changePercent: number;
  direction: TrendDirection;
  momentum: string;
  catalysts: string[];
};

export type RiskBannerItem = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
};

export type OverviewFixture = {
  asOf: string;
  lead: string;
  scenario: string;
  indices: IndexStripItem[];
  news: NewsItem[];
  sectors: SectorStrengthItem[];
  risks: RiskBannerItem[];
  heatmap: Array<{
    label: string;
    score: number;
    changePercent: number;
  }>;
};

export type WatchlistFolderNode = {
  id: string;
  label: string;
  count: number;
  description: string;
  children?: WatchlistFolderNode[];
};

export type RadarColumnKey =
  | "symbol"
  | "name"
  | "price"
  | "changePercent"
  | "score"
  | "volumeRatio"
  | "relativeStrength"
  | "sector"
  | "nextEvent"
  | "thesis";

export type WatchlistRow = {
  symbol: string;
  name: string;
  sector: string;
  folderId: string;
  price: number;
  changePercent: number;
  volumeRatio: number;
  relativeStrength: number;
  score: number;
  nextEvent: string;
  thesis: string;
  condition: string;
};

export type SectorInsightCard = {
  sector: string;
  score: number;
  thesis: string;
  catalyst: string;
  topPick: string;
};

export type ScheduleItem = {
  time: string;
  title: string;
  note: string;
};

export type BrokerReportItem = {
  house: string;
  symbol: string;
  stance: string;
  summary: string;
};

export type TopPickItem = {
  symbol: string;
  reason: string;
  score: number;
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
};

export type PricePoint = {
  label: string;
  close: number;
  volume: number;
};

export type ChartGuide = {
  label: string;
  value: number;
  tone: Tone;
};

export type RulePreset = {
  label: string;
  description: string;
  enabled: boolean;
};

export type ScoreBreakdownItem = {
  label: string;
  score: number;
  summary: string;
};

export type FlowItem = {
  label: string;
  value: string;
  delta: string;
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
};

export type StockFixture = {
  symbol: string;
  name: string;
  exchange: string;
  price: number;
  changePercent: number;
  marketCap: string;
  thesis: string;
  chartPoints: PricePoint[];
  indicatorGuides: ChartGuide[];
  rulePresets: RulePreset[];
  scoreBreakdown: ScoreBreakdownItem[];
  flows: FlowItem[];
  shortOptionMetrics: ShortOptionMetric[];
  issues: StockIssueItem[];
  relatedSymbols: string[];
};

export type HistoryEvent = {
  id: string;
  date: string;
  title: string;
  category: string;
  summary: string;
  reaction: string;
  tone: Tone;
};

export type MoveReason = {
  label: string;
  description: string;
  tone: Tone;
};

export type OverlapIndicator = {
  label: string;
  detail: string;
  tone: Tone;
};

export type HistoryFixture = {
  symbol: string;
  range: string;
  presets: string[];
  chartPoints: PricePoint[];
  events: HistoryEvent[];
  moveReasons: MoveReason[];
  overlaps: OverlapIndicator[];
};
