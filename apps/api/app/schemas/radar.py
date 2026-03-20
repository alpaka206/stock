from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import AnalysisEnvelope, SourcedText


class FolderNode(BaseModel):
    id: str
    label: str
    count: int
    description: str
    tags: list[str] = Field(default_factory=list)
    children: list["FolderNode"] = Field(default_factory=list)


class WatchlistRow(BaseModel):
    symbol: str
    name: str
    securityCode: str
    sector: str
    folderId: str
    tags: list[str] = Field(default_factory=list)
    price: float
    changePercent: float
    volumeRatio: float
    relativeStrength: float
    score: float
    nextEvent: str
    thesis: str
    condition: str
    sourceRefIds: list[str] = Field(default_factory=list)


class SectorCard(BaseModel):
    sector: str
    score: float
    thesis: str
    catalyst: str
    topPick: str
    sourceRefIds: list[str] = Field(default_factory=list)


class BrokerReportItem(BaseModel):
    sector: str = ""
    house: str
    symbol: str
    stance: str
    summary: str
    sourceRefIds: list[str] = Field(default_factory=list)


class KeyScheduleItem(BaseModel):
    sector: str = ""
    time: str
    title: str
    note: str
    sourceRefIds: list[str] = Field(default_factory=list)


class KeyIssueItem(BaseModel):
    headline: str
    summary: str
    impact: str
    sector: str = ""
    sourceRefIds: list[str] = Field(default_factory=list)


class TopPickItem(BaseModel):
    sector: str = ""
    symbol: str
    reason: str
    score: float
    sourceRefIds: list[str] = Field(default_factory=list)


class RadarResponse(AnalysisEnvelope):
    selectedSectorSummary: SourcedText
    folderTree: list[FolderNode] = Field(default_factory=list)
    watchlistRows: list[WatchlistRow] = Field(default_factory=list)
    sectorCards: list[SectorCard] = Field(default_factory=list)
    brokerReports: list[BrokerReportItem] = Field(default_factory=list)
    keySchedule: list[KeyScheduleItem] = Field(default_factory=list)
    keyIssues: list[KeyIssueItem] = Field(default_factory=list)
    topPicks: list[TopPickItem] = Field(default_factory=list)
