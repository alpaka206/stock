from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.services.prompt_loader import PromptBundle


class ResearchProvider(ABC):
    @abstractmethod
    async def get_overview(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_radar(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_stock_detail(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_history(
        self,
        *,
        symbol: str | None,
        range: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        prompt_bundle: PromptBundle,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_news(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_calendar(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        raise NotImplementedError
