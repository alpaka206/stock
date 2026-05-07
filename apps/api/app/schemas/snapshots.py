from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ResearchSnapshotStance = Literal["bullish", "neutral", "bearish"]
ResearchSnapshotConviction = Literal["low", "medium", "high"]


class ResearchSnapshotBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    securityCode: str
    sector: str
    note: str
    stance: ResearchSnapshotStance
    conviction: ResearchSnapshotConviction
    price: float
    changePercent: float
    score: float
    thesis: str
    selectedEventTitle: str | None = None
    selectedEventDate: str | None = None
    activeRuleLabels: list[str] = Field(default_factory=list)
    presetName: str = ""


class ResearchSnapshot(ResearchSnapshotBase):
    id: str
    createdAt: str


class ResearchSnapshotCreate(ResearchSnapshotBase):
    id: str | None = None
    createdAt: str | None = None


class SnapshotListResponse(BaseModel):
    snapshots: list[ResearchSnapshot]


class SnapshotMutationResponse(BaseModel):
    snapshot: ResearchSnapshot


class SnapshotDeleteResponse(BaseModel):
    deleted: bool
    id: str
