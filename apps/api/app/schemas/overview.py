from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, SourcedText


class SectorStrengthItem(BaseModel):
    sector: str
    score: float
    summary: str
    changePercent: float | None = None
    sourceRefIds: list[str]


class NotableNewsItem(BaseModel):
    headline: str
    source: str
    summary: str = ""
    impact: str
    publishedAt: str
    url: str
    sourceRefIds: list[str]


class BenchmarkSnapshotItem(BaseModel):
    label: str
    symbol: str
    category: str
    value: float
    changePercent: float
    note: str
    sourceRefIds: list[str]


class OverviewResponse(AnalysisEnvelope):
    benchmarkSnapshot: list[BenchmarkSnapshotItem] = Field(default_factory=list)
    marketSummary: SourcedText
    drivers: list[SourcedText]
    risks: list[SourcedText]
    sectorStrength: list[SectorStrengthItem]
    notableNews: list[NotableNewsItem]
