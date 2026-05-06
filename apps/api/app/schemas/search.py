from __future__ import annotations

from pydantic import BaseModel, Field


class InstrumentSearchItem(BaseModel):
    symbol: str
    name: str
    securityCode: str
    aliases: list[str] = Field(default_factory=list)
    sector: str = ""
    exchange: str = ""


class InstrumentSearchResponse(BaseModel):
    items: list[InstrumentSearchItem] = Field(default_factory=list)
