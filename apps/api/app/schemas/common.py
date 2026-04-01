from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    id: str
    title: str
    kind: Literal[
        "market_data",
        "news",
        "fundamentals",
        "economic",
        "internal_config",
        "mock",
    ]
    publisher: str
    publishedAt: datetime
    url: str = ""
    sourceKey: str = ""
    symbol: str = ""


class MissingDataItem(BaseModel):
    field: str
    reason: str
    expectedSource: str


class Confidence(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    label: Literal["low", "medium", "high"]
    rationale: str


class SourcedText(BaseModel):
    text: str
    sourceRefIds: list[str] = Field(default_factory=list)


class AnalysisEnvelope(BaseModel):
    asOf: datetime
    sourceRefs: list[SourceRef]
    missingData: list[MissingDataItem]
    confidence: Confidence
