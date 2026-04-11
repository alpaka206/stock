from __future__ import annotations

from datetime import datetime, timezone

from app.services.prompt_loader import PromptBundle
from app.services.providers.mock import MockResearchProvider, _base_envelope, _sourced_text


class ExtendedMockResearchProvider(MockResearchProvider):
    async def get_news(self, *, prompt_bundle: PromptBundle) -> dict[str, object]:
        payload = _base_envelope()
        payload.update(
            {
                "marketSummary": _sourced_text("해외 메인 뉴스, 관심종목 뉴스, 국내 공시를 한 화면에서 보는 개발용 mock 뉴스 피드입니다."),
                "newsDrivers": [
                    _sourced_text("해외 헤드라인을 먼저 읽고, 관심종목과 국내 공시를 뒤이어 확인합니다."),
                    _sourced_text("실제 API 연결 전까지는 mock 데이터임을 전제로 봐야 합니다."),
                ],
                "featuredNews": [
                    {
                        "id": "mock-featured-1",
                        "headline": "AI 투자 확대 기대가 대형 반도체 강세를 이끌었습니다.",
                        "source": "mock",
                        "summary": "해외 메인 뉴스 섹션에서 읽을 대표 헤드라인입니다.",
                        "impact": "긍정",
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
                        "headline": "NVIDIA 관련 공급망 체크 포인트가 다시 부각됐습니다.",
                        "source": "mock",
                        "summary": "관심종목 중심으로 추려 보는 뉴스 예시입니다.",
                        "impact": "관심",
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
                        "headline": "국내 공시 예시",
                        "source": "mock",
                        "summary": "국내 공시 API 연동 전 mock 섹션입니다.",
                        "impact": "공시",
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
                "calendarSummary": _sourced_text("실적, IPO, 국내 공시를 한 흐름으로 보는 개발용 mock 캘린더입니다."),
                "highlights": [
                    {
                        "label": "관심종목 실적",
                        "value": "2건",
                        "detail": "NVDA, AVGO",
                        "tone": "positive",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "IPO 캘린더",
                        "value": "1건",
                        "detail": "미국 신규 상장 체크",
                        "tone": "neutral",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "watchlistEvents": [
                    {
                        "id": "mock-calendar-watchlist-1",
                        "title": "NVDA 실적 예정",
                        "category": "earnings",
                        "market": "watchlist",
                        "date": "2026-04-18",
                        "time": "예정",
                        "summary": "관심종목 실적 체크 예시입니다.",
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
                        "summary": "글로벌 IPO 일정 예시입니다.",
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
                        "title": "국내 공시 예시",
                        "category": "disclosure",
                        "market": "domestic",
                        "date": "2026-04-17",
                        "time": "공시",
                        "summary": "국내 공시 연동 전 mock 카드입니다.",
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
