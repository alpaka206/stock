from __future__ import annotations

from datetime import datetime, timezone

from app.services.prompt_loader import PromptBundle
from app.services.providers.mock import MockResearchProvider, _base_envelope, _sourced_text


class ExtendedMockResearchProvider(MockResearchProvider):
    async def get_news(self, *, prompt_bundle: PromptBundle) -> dict[str, object]:
        payload = _base_envelope()
        payload.update(
            {
                "marketSummary": _sourced_text("\ud574\uc678 \uba54\uc778 \ub274\uc2a4, \uad00\uc2ec\uc885\ubaa9 \ub274\uc2a4, \uad6d\ub0b4 \uacf5\uc2dc\ub97c \ud55c \ud654\uba74\uc5d0\uc11c \ubcf4\ub294 \uac1c\ubc1c\uc6a9 mock \ub274\uc2a4 \ud53c\ub4dc\uc785\ub2c8\ub2e4."),
                "newsDrivers": [
                    _sourced_text("\ud574\uc678 \ud5e4\ub4dc\ub77c\uc778\uc744 \uba3c\uc800 \uc77d\uace0, \uad00\uc2ec\uc885\ubaa9\uacfc \uad6d\ub0b4 \uacf5\uc2dc\ub97c \ub4a4\uc774\uc5b4 \ud655\uc778\ud569\ub2c8\ub2e4."),
                    _sourced_text("\uc2e4\uc81c API \uc5f0\uacb0 \uc804\uae4c\uc9c0\ub294 mock \ub370\uc774\ud130\uc784\uc744 \uc804\uc81c\ub85c \ubd10\uc57c \ud569\ub2c8\ub2e4."),
                ],
                "featuredNews": [
                    {
                        "id": "mock-featured-1",
                        "headline": "AI \ud22c\uc790 \ud655\ub300 \uae30\ub300\uac00 \ub300\ud615 \ubc18\ub3c4\uccb4 \uac15\uc138\ub97c \uc774\ub04c\uc5c8\uc2b5\ub2c8\ub2e4.",
                        "source": "mock",
                        "summary": "\ud574\uc678 \uba54\uc778 \ub274\uc2a4 \uc139\uc158\uc5d0\uc11c \uc77d\uc744 \ub300\ud45c \ud5e4\ub4dc\ub77c\uc778\uc785\ub2c8\ub2e4.",
                        "impact": "\uae0d\uc815",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "symbol": "NVDA",
                        "market": "global",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "watchlistNews": [
                    {
                        "id": "mock-watchlist-1",
                        "headline": "NVIDIA \uad00\ub828 \uacf5\uae09\ub9dd \uccb4\ud06c \ud3ec\uc778\ud2b8\uac00 \ub2e4\uc2dc \ubd80\uac01\ub410\uc2b5\ub2c8\ub2e4.",
                        "source": "mock",
                        "summary": "\uad00\uc2ec\uc885\ubaa9 \uc911\uc2ec\uc73c\ub85c \ucd94\ub824 \ubcf4\ub294 \ub274\uc2a4 \uc608\uc2dc\uc785\ub2c8\ub2e4.",
                        "impact": "\uad00\uc2ec",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "symbol": "NVDA",
                        "market": "watchlist",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "domesticDisclosures": [
                    {
                        "id": "mock-domestic-1",
                        "headline": "\uad6d\ub0b4 \uacf5\uc2dc \uc608\uc2dc",
                        "source": "mock",
                        "summary": "\uad6d\ub0b4 \uacf5\uc2dc API \uc5f0\ub3d9 \uc804 mock \uc139\uc158\uc785\ub2c8\ub2e4.",
                        "impact": "\uacf5\uc2dc",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "symbol": "005930",
                        "market": "domestic",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
            }
        )
        return payload

    async def get_calendar(self, *, prompt_bundle: PromptBundle) -> dict[str, object]:
        payload = _base_envelope()
        payload.update(
            {
                "calendarSummary": _sourced_text("\uc2e4\uc801, IPO, \uad6d\ub0b4 \uacf5\uc2dc\ub97c \ud55c \ud750\ub984\uc73c\ub85c \ubcf4\ub294 \uac1c\ubc1c\uc6a9 mock \uce98\ub9b0\ub354\uc785\ub2c8\ub2e4."),
                "highlights": [
                    {
                        "label": "\uad00\uc2ec\uc885\ubaa9 \uc2e4\uc801",
                        "value": "2\uac74",
                        "detail": "NVDA, AVGO",
                        "tone": "positive",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "IPO \uce98\ub9b0\ub354",
                        "value": "1\uac74",
                        "detail": "\ubbf8\uad6d \uc2e0\uaddc \uc0c1\uc7a5 \uccb4\ud06c",
                        "tone": "neutral",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "watchlistEvents": [
                    {
                        "id": "mock-calendar-watchlist-1",
                        "title": "NVDA \uc2e4\uc801 \uc608\uc815",
                        "category": "earnings",
                        "market": "watchlist",
                        "date": "2026-04-18",
                        "time": "\uc608\uc815",
                        "summary": "\uad00\uc2ec\uc885\ubaa9 \uc2e4\uc801 \uccb4\ud06c \uc608\uc2dc\uc785\ub2c8\ub2e4.",
                        "source": "mock",
                        "symbol": "NVDA",
                        "url": "",
                        "tone": "neutral",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "marketEvents": [
                    {
                        "id": "mock-calendar-market-1",
                        "title": "Sample IPO",
                        "category": "ipo",
                        "market": "global",
                        "date": "2026-04-22",
                        "time": "NASDAQ",
                        "summary": "\uae00\ub85c\ubc8c IPO \uc77c\uc815 \uc608\uc2dc\uc785\ub2c8\ub2e4.",
                        "source": "mock",
                        "symbol": "SAMP",
                        "url": "",
                        "tone": "neutral",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "domesticEvents": [
                    {
                        "id": "mock-calendar-domestic-1",
                        "title": "\uad6d\ub0b4 \uacf5\uc2dc \uc608\uc2dc",
                        "category": "disclosure",
                        "market": "domestic",
                        "date": "2026-04-17",
                        "time": "\uacf5\uc2dc",
                        "summary": "\uad6d\ub0b4 \uacf5\uc2dc \uc5f0\ub3d9 \uc804 mock \uce74\ub4dc\uc785\ub2c8\ub2e4.",
                        "source": "mock",
                        "symbol": "005930",
                        "url": "",
                        "tone": "neutral",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
            }
        )
        return payload
