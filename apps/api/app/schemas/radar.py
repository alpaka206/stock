from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import AnalysisEnvelope, SourcedText


class KeyScheduleItem(BaseModel):
    time: str
    title: str
    note: str
    sourceRefIds: list[str]


class KeyIssueItem(BaseModel):
    headline: str
    summary: str
    impact: str
    sourceRefIds: list[str]


class TopPickItem(BaseModel):
    symbol: str
    reason: str
    score: float
    sourceRefIds: list[str]


class WatchlistHighlightItem(BaseModel):
    symbol: str
    thesis: str
    condition: str
    price: float
    changePercent: float
    score: float
    sourceRefIds: list[str]


class RadarResponse(AnalysisEnvelope):
    selectedSectorSummary: SourcedText
    reportSummary: list[SourcedText]
    keySchedule: list[KeyScheduleItem]
    keyIssues: list[KeyIssueItem]
    topPicks: list[TopPickItem]
    watchlistHighlights: list[WatchlistHighlightItem]
