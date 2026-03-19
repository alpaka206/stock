from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import AnalysisEnvelope, SourcedText


class TurningPoint(BaseModel):
    date: str
    summary: str
    sourceRefIds: list[str]


class OverlappingIndicator(BaseModel):
    name: str
    interpretation: str
    sourceRefIds: list[str]


class EventTimelineItem(BaseModel):
    date: str
    title: str
    source: str
    url: str
    sourceRefIds: list[str]


class HistoryResponse(AnalysisEnvelope):
    moveSummary: SourcedText
    turningPoints: list[TurningPoint]
    overlappingIndicators: list[OverlappingIndicator]
    eventTimelineSummary: list[EventTimelineItem]
    analogsOrPatterns: list[SourcedText]
