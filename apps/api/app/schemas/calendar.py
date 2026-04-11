from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, SourcedText


class CalendarHighlight(BaseModel):
    label: str
    value: str
    detail: str
    tone: Literal["positive", "negative", "neutral"]
    sourceRefIds: list[str] = Field(default_factory=list)


class CalendarEventItem(BaseModel):
    id: str
    title: str
    category: Literal["earnings", "ipo", "macro", "disclosure", "news"]
    market: Literal["watchlist", "global", "domestic"]
    date: str
    time: str
    summary: str
    source: str
    symbol: str = ""
    url: str = ""
    tone: Literal["positive", "negative", "neutral"]
    sourceRefIds: list[str] = Field(default_factory=list)


class CalendarResponse(AnalysisEnvelope):
    calendarSummary: SourcedText
    highlights: list[CalendarHighlight]
    watchlistEvents: list[CalendarEventItem]
    marketEvents: list[CalendarEventItem]
    domesticEvents: list[CalendarEventItem]
