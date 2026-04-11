from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, SourcedText


class NewsFeedItem(BaseModel):
    id: str
    headline: str
    source: str
    summary: str
    impact: str
    publishedAt: str
    url: str = ""
    symbol: str = ""
    market: Literal["global", "watchlist", "domestic"]
    sourceRefIds: list[str] = Field(default_factory=list)


class NewsResponse(AnalysisEnvelope):
    marketSummary: SourcedText
    newsDrivers: list[SourcedText]
    featuredNews: list[NewsFeedItem]
    watchlistNews: list[NewsFeedItem]
    domesticDisclosures: list[NewsFeedItem]
