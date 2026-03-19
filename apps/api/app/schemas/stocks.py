from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import AnalysisEnvelope, SourcedText


class ScoreBreakdown(BaseModel):
    technical: float
    flow: float
    catalyst: float
    risk: float


class ScoreCard(BaseModel):
    total: float
    breakdown: ScoreBreakdown
    sourceRefIds: list[str]


class SignalSummary(BaseModel):
    positive: list[SourcedText]
    negative: list[SourcedText]


class ChartNotes(BaseModel):
    trend: SourcedText
    support: SourcedText
    resistance: SourcedText


class StockDetailResponse(AnalysisEnvelope):
    score: ScoreCard
    signals: SignalSummary
    flowSummary: SourcedText
    optionsShortSummary: SourcedText
    issueSummary: list[SourcedText]
    chartNotes: ChartNotes
    risks: list[SourcedText]
