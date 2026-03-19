from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import AnalysisEnvelope, SourcedText


class SectorStrengthItem(BaseModel):
    sector: str
    score: float
    summary: str
    sourceRefIds: list[str]


class NotableNewsItem(BaseModel):
    headline: str
    source: str
    impact: str
    publishedAt: str
    url: str
    sourceRefIds: list[str]


class OverviewResponse(AnalysisEnvelope):
    marketSummary: SourcedText
    drivers: list[SourcedText]
    risks: list[SourcedText]
    sectorStrength: list[SectorStrengthItem]
    notableNews: list[NotableNewsItem]
