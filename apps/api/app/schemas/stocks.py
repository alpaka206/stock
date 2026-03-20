from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, Confidence

Tone = Literal["positive", "negative", "neutral"]


class InstrumentInfo(BaseModel):
    symbol: str
    name: str
    exchange: str
    securityCode: str
    sector: str
    marketCap: str


class PriceSeriesPoint(BaseModel):
    date: str
    label: str
    close: float
    volume: float


class ChartMarker(BaseModel):
    id: str
    label: str
    tone: Tone
    date: str = ""
    pointLabel: str = ""
    title: str = ""
    detail: str = ""
    href: str = ""


class IndicatorGuide(BaseModel):
    id: str
    label: str
    value: float
    tone: Tone
    description: str = ""
    enabled: bool = True


class RulePresetDefinition(BaseModel):
    id: str
    label: str
    description: str
    enabledByDefault: bool
    tone: Tone | None = None


class ScoreBreakdownItem(BaseModel):
    label: str
    score: float
    summary: str


class ScoreSummary(BaseModel):
    total: float
    confidence: Confidence
    breakdown: list[ScoreBreakdownItem] = Field(default_factory=list)


class MetricCard(BaseModel):
    label: str
    value: str
    detail: str
    tone: Tone


class AvailabilityState(BaseModel):
    label: str
    reason: str
    expectedSource: str = ""


class IssueCard(BaseModel):
    title: str
    source: str
    summary: str
    tone: Tone
    category: str = ""
    href: str = ""
    sourceRefIds: list[str] = Field(default_factory=list)


class StockDetailResponse(AnalysisEnvelope):
    instrument: InstrumentInfo
    latestPrice: float
    changePercent: float
    thesis: str
    priceSeries: list[PriceSeriesPoint] = Field(default_factory=list)
    eventMarkers: list[ChartMarker] = Field(default_factory=list)
    indicatorGuides: list[IndicatorGuide] = Field(default_factory=list)
    rulePresetDefinitions: list[RulePresetDefinition] = Field(default_factory=list)
    scoreSummary: ScoreSummary
    flowMetrics: list[MetricCard] = Field(default_factory=list)
    flowUnavailable: AvailabilityState | None = None
    optionsShortMetrics: list[MetricCard] = Field(default_factory=list)
    optionsUnavailable: AvailabilityState | None = None
    issueCards: list[IssueCard] = Field(default_factory=list)
    relatedSymbols: list[str] = Field(default_factory=list)
