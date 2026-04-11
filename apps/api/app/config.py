from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel, Field, field_validator


DEFAULT_OVERVIEW_BENCHMARKS = {
    "SPY": "S&P 500",
    "QQQ": "NASDAQ 100",
    "SMH": "반도체",
    "IWM": "?? 2000",
}

DEFAULT_SECTOR_PROXIES = {
    "XLK": "기술주",
    "XLF": "??",
    "XLE": "에너지",
}

DEFAULT_RADAR_SYMBOLS = ["NVDA", "AMD", "AVGO", "MSFT", "CRWD"]
DEFAULT_RADAR_SECTORS = {
    "NVDA": "반도체",
    "AMD": "반도체",
    "AVGO": "반도체",
    "MSFT": "소프트웨어",
    "CRWD": "사이버보안",
}
ALLOWED_PROVIDERS = {"mock", "real"}
ALLOWED_LLM_PROVIDERS = {"auto", "openai", "gemini", "none"}


def _parse_csv(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    items = [item.strip().upper() for item in value.split(",") if item.strip()]
    return items or fallback


def _parse_symbol_map(value: str | None, fallback: dict[str, str]) -> dict[str, str]:
    if not value:
        return fallback

    pairs: dict[str, str] = {}
    for chunk in value.split(","):
        if ":" not in chunk:
            continue
        symbol, label = chunk.split(":", 1)
        if symbol.strip() and label.strip():
            pairs[symbol.strip().upper()] = label.strip()
    return pairs or fallback


class Settings(BaseModel):
    app_name: str = "Stock Research Workspace API"
    app_version: str = "0.1.0"
    default_provider: str = Field(
        default_factory=lambda: os.getenv("STOCK_API_PROVIDER", "mock")
    )
    llm_provider: str = Field(
        default_factory=lambda: os.getenv("RESEARCH_LLM_PROVIDER", "auto")
    )
    prompt_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "prompts"
    )
    request_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("STOCK_API_TIMEOUT_SECONDS", "12"))
    )
    provider_cache_ttl_seconds: int = Field(
        default_factory=lambda: int(os.getenv("STOCK_API_CACHE_TTL_SECONDS", "60"))
    )
    alpha_vantage_api_key: str | None = Field(
        default_factory=lambda: os.getenv("ALPHA_VANTAGE_API_KEY")
    )
    alpha_vantage_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "ALPHA_VANTAGE_BASE_URL", "https://www.alphavantage.co/query"
        )
    )
    opendart_api_key: str | None = Field(
        default_factory=lambda: os.getenv("OPENDART_API_KEY")
    )
    opendart_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "OPENDART_BASE_URL", "https://opendart.fss.or.kr/api"
        )
    )
    openai_api_key: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    openai_model: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-5-mini")
    )
    gemini_api_key: str | None = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY")
    )
    gemini_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    gemini_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/models",
        )
    )
    overview_benchmarks: dict[str, str] = Field(
        default_factory=lambda: _parse_symbol_map(
            os.getenv("STOCK_OVERVIEW_BENCHMARKS"), DEFAULT_OVERVIEW_BENCHMARKS
        )
    )
    sector_proxies: dict[str, str] = Field(
        default_factory=lambda: _parse_symbol_map(
            os.getenv("STOCK_SECTOR_PROXIES"), DEFAULT_SECTOR_PROXIES
        )
    )
    radar_symbols: list[str] = Field(
        default_factory=lambda: _parse_csv(
            os.getenv("STOCK_RADAR_SYMBOLS"), DEFAULT_RADAR_SYMBOLS
        )[:5]
    )
    radar_sector_map: dict[str, str] = Field(
        default_factory=lambda: _parse_symbol_map(
            os.getenv("STOCK_RADAR_SECTORS"), DEFAULT_RADAR_SECTORS
        )
    )

    @field_validator("default_provider")
    @classmethod
    def validate_default_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_PROVIDERS:
            allowed = ", ".join(sorted(ALLOWED_PROVIDERS))
            raise ValueError(f"STOCK_API_PROVIDER must be one of: {allowed}.")
        return normalized

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_LLM_PROVIDERS:
            allowed = ", ".join(sorted(ALLOWED_LLM_PROVIDERS))
            raise ValueError(f"RESEARCH_LLM_PROVIDER must be one of: {allowed}.")
        return normalized


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
