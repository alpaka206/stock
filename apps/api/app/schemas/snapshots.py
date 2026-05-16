from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ResearchSnapshotStance = Literal["bullish", "neutral", "bearish"]
ResearchSnapshotConviction = Literal["low", "medium", "high"]


class ResearchSnapshotBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=160)
    exchange: str = Field(min_length=1, max_length=40)
    securityCode: str = Field(min_length=1, max_length=40)
    sector: str = Field(min_length=1, max_length=80)
    note: str = Field(min_length=1, max_length=4000)
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

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.upper()


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
