from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, SourcedText

Tone = Literal["positive", "negative", "neutral"]


class HistoryRangeOption(BaseModel):
    value: str
    label: str


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


class HistoryEventItem(BaseModel):
    id: str
    date: str
    title: str
    category: str
    summary: str
    reaction: str
    tone: Tone
    source: str = ""
    url: str = ""
    sourceRefIds: list[str] = Field(default_factory=list)


class MoveReasonItem(BaseModel):
    label: str
    description: str
    tone: Tone
    relatedDate: str = ""
    sourceRefIds: list[str] = Field(default_factory=list)


class OverlappingIndicator(BaseModel):
    label: str
    detail: str
    tone: Tone
    relatedDate: str = ""
    sourceRefIds: list[str] = Field(default_factory=list)


class HistoryResponse(AnalysisEnvelope):
    symbol: str
    rangeLabel: str
    availableRanges: list[HistoryRangeOption] = Field(default_factory=list)
    priceSeries: list[PriceSeriesPoint] = Field(default_factory=list)
    eventMarkers: list[ChartMarker] = Field(default_factory=list)
    eventTimeline: list[HistoryEventItem] = Field(default_factory=list)
    moveSummary: SourcedText
    moveReasons: list[MoveReasonItem] = Field(default_factory=list)
    overlappingIndicators: list[OverlappingIndicator] = Field(default_factory=list)
    analogsOrPatterns: list[SourcedText] = Field(default_factory=list)
