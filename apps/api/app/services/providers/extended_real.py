from __future__ import annotations

from datetime import datetime, timezone

from app.config import Settings
from app.services.clients.open_dart import OpenDartClient
from app.services.prompt_loader import PromptBundle
from app.services.providers.real import RealResearchProvider
from app.services.source_refs import build_source_ref


class ExtendedRealResearchProvider(RealResearchProvider):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.disclosure_data = OpenDartClient(
            api_key=settings.opendart_api_key,
            base_url=settings.opendart_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )

    async def get_news(self, *, prompt_bundle: PromptBundle) -> dict[str, object]:
        source_refs: list[dict[str, object]] = []
        missing_data: list[dict[str, str]] = []
        featured_news = await self._build_news_items(
            source_refs=source_refs,
            field="news.featured",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
        )
        watchlist_news = await self._build_news_items(
            source_refs=source_refs,
            field="news.watchlist",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=self.settings.radar_symbols,
        )
        disclosures = await self._safe_fetch(
            field="news.domesticDisclosures",
            expected_source="OpenDART list.json",
            missing_data=missing_data,
            fetcher=self.disclosure_data.get_recent_disclosures,
            days=5,
            page_count=12,
            corp_cls="Y",
        )
        domestic_disclosures = self._build_domestic_disclosure_items(disclosures or [], source_refs)
        payload = {
            "marketSummary": {
                "text": self._build_news_market_summary(featured_news, watchlist_news, domestic_disclosures),
                "sourceRefIds": self._merge_ref_ids(featured_news, watchlist_news, domestic_disclosures),
            },
            "newsDrivers": self._build_news_drivers(featured_news, watchlist_news, domestic_disclosures),
            "featuredNews": self._build_news_feed_items(featured_news, market="global"),
            "watchlistNews": self._build_news_feed_items(watchlist_news, market="watchlist"),
            "domesticDisclosures": domestic_disclosures,
        }
        return self._finalize_payload(payload, source_refs, missing_data)

    async def get_calendar(self, *, prompt_bundle: PromptBundle) -> dict[str, object]:
        source_refs: list[dict[str, object]] = []
        missing_data: list[dict[str, str]] = []
        earnings_rows = await self._safe_fetch(
            field="calendar.watchlistEarnings",
            expected_source="Alpha Vantage EARNINGS_CALENDAR",
            missing_data=missing_data,
            fetcher=self.market_data.get_earnings_calendar,
            horizon="3month",
        )
        ipo_rows = await self._safe_fetch(
            field="calendar.ipo",
            expected_source="Alpha Vantage IPO_CALENDAR",
            missing_data=missing_data,
            fetcher=self.market_data.get_ipo_calendar,
        )
        treasury = await self._safe_fetch(
            field="calendar.treasuryYield10Y",
            expected_source="Alpha Vantage TREASURY_YIELD",
            missing_data=missing_data,
            fetcher=self.market_data.get_treasury_yield,
        )
        watchlist_news = await self._build_news_items(
            source_refs=source_refs,
            field="calendar.watchlistNews",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=self.settings.radar_symbols,
        )
        disclosures = await self._safe_fetch(
            field="calendar.domesticDisclosures",
            expected_source="OpenDART list.json",
            missing_data=missing_data,
            fetcher=self.disclosure_data.get_recent_disclosures,
            days=7,
            page_count=10,
            corp_cls="Y",
        )
        watchlist_events = self._build_watchlist_earnings_events(earnings_rows or [], source_refs)
        news_events = self._build_watchlist_news_events(watchlist_news)
        market_events = self._build_ipo_events(ipo_rows or [], source_refs)
        domestic_events = self._build_domestic_calendar_events(disclosures or [], source_refs)
        payload = {
            "calendarSummary": {
                "text": self._build_calendar_summary(watchlist_events, market_events, domestic_events, treasury),
                "sourceRefIds": self._merge_ref_ids(watchlist_events, market_events, domestic_events),
            },
            "highlights": self._build_calendar_highlights(
                watchlist_events=watchlist_events,
                market_events=market_events,
                domestic_events=domestic_events,
                treasury=treasury,
                source_refs=source_refs,
            ),
            "watchlistEvents": (watchlist_events + news_events)[:8],
            "marketEvents": market_events[:8],
            "domesticEvents": domestic_events[:8],
        }
        return self._finalize_payload(payload, source_refs, missing_data)

    def _build_news_market_summary(self, featured_news, watchlist_news, domestic_disclosures) -> str:
        featured = featured_news[0]["title"] if featured_news else "\ud574\uc678 \ud5e4\ub4dc\ub77c\uc778\uc774 \uc544\uc9c1 \ubd80\uc871\ud569\ub2c8\ub2e4"
        watchlist = watchlist_news[0]["title"] if watchlist_news else "\uad00\uc2ec\uc885\ubaa9 \ub274\uc2a4\uac00 \uc544\uc9c1 \uc801\uc2b5\ub2c8\ub2e4"
        domestic = domestic_disclosures[0]["headline"] if domestic_disclosures else "OpenDART \uc5f0\ub3d9 \ub610\ub294 \ucd5c\uc2e0 \uacf5\uc2dc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4"
        return f"\ud574\uc678 \uba54\uc778 \ud5e4\ub4dc\ub77c\uc778\uc740 '{featured}' \uc911\uc2ec\uc73c\ub85c \uc6c0\uc9c1\uc774\uace0, \uad00\uc2ec\uc885\ubaa9 \ud750\ub984\uc740 '{watchlist}'\ub97c \uc6b0\uc120 \ud655\uc778\ud560 \uad6c\uac04\uc785\ub2c8\ub2e4. \uad6d\ub0b4\ub294 '{domestic}' \uacf5\uc2dc\ub97c \ud568\uaed8 \ubd10\uc57c \ud569\ub2c8\ub2e4."

    def _build_news_drivers(self, featured_news, watchlist_news, domestic_disclosures):
        items = []
        if featured_news:
            items.append({
                "text": f"\ud574\uc678 \ud5e4\ub4dc\ub77c\uc778\uc740 {featured_news[0]['source']} \ubc1c {featured_news[0]['title']}\ub97c \uc6b0\uc120 \ud655\uc778\ud569\ub2c8\ub2e4.",
                "sourceRefIds": featured_news[0].get("sourceRefIds", []),
            })
        if watchlist_news:
            symbol = watchlist_news[0].get("tickers", [""])[0] if watchlist_news[0].get("tickers") else "\ud575\uc2ec \uc2ec\ubcfc"
            items.append({
                "text": f"\uad00\uc2ec\uc885\ubaa9\uc740 {symbol} \uad00\ub828 \ub274\uc2a4 \ubc18\uc751\uc774 \uac00\uc7a5 \ube60\ub985\ub2c8\ub2e4.",
                "sourceRefIds": watchlist_news[0].get("sourceRefIds", []),
            })
        if domestic_disclosures:
            items.append({
                "text": f"\uad6d\ub0b4\ub294 {domestic_disclosures[0]['headline']} \uacf5\uc2dc\ub97c \uccb4\ud06c \ud3ec\uc778\ud2b8\ub85c \ub461\ub2c8\ub2e4.",
                "sourceRefIds": domestic_disclosures[0].get("sourceRefIds", []),
            })
        return items or [{"text": "\ud604\uc7ac \uc5f0\uacb0\ub41c \ub274\uc2a4/\uacf5\uc2dc \ub370\uc774\ud130\uac00 \ucda9\ubd84\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.", "sourceRefIds": []}]

    def _build_news_feed_items(self, articles, *, market: str):
        items = []
        for index, article in enumerate(articles[:8]):
            symbol = article.get("tickers", [""])[0] if article.get("tickers") else ""
            items.append({
                "id": f"{market}-news-{index + 1}",
                "headline": article.get("title", ""),
                "source": article.get("source", "Alpha Vantage"),
                "summary": article.get("summary", ""),
                "impact": self._impact_from_sentiment(article.get("sentimentLabel", "")),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", ""),
                "symbol": symbol,
                "market": market,
                "sourceRefIds": article.get("sourceRefIds", []),
            })
        return items

    def _build_domestic_disclosure_items(self, disclosures, source_refs):
        items = []
        for index, disclosure in enumerate(disclosures[:8]):
            ref = build_source_ref(
                title=disclosure.get("reportName", "\uad6d\ub0b4 \uacf5\uc2dc"),
                kind="disclosure",
                publisher="OpenDART",
                published_at=disclosure.get("receiptDate", ""),
                source_key="opendart::list",
                url=disclosure.get("url", ""),
                symbol=disclosure.get("stockCode", ""),
            )
            source_refs.append(ref)
            items.append({
                "id": f"domestic-disclosure-{index + 1}",
                "headline": disclosure.get("corpName", "\uad6d\ub0b4 \uacf5\uc2dc"),
                "source": "OpenDART",
                "summary": disclosure.get("reportName", ""),
                "impact": "\uacf5\uc2dc",
                "publishedAt": self._to_iso(disclosure.get("receiptDate", "")),
                "url": disclosure.get("url", ""),
                "symbol": disclosure.get("stockCode", ""),
                "market": "domestic",
                "sourceRefIds": [ref["id"]],
            })
        return items

    def _build_watchlist_earnings_events(self, rows, source_refs):
        events = []
        allowed = set(self.settings.radar_symbols)
        for index, row in enumerate([item for item in rows if item.get("symbol") in allowed][:8]):
            ref = build_source_ref(
                title=f"{row['symbol']} earnings calendar",
                kind="fundamentals",
                publisher="Alpha Vantage",
                published_at=row.get("reportDate", ""),
                source_key="alpha_vantage::EARNINGS_CALENDAR",
                symbol=row.get("symbol", ""),
            )
            source_refs.append(ref)
            events.append({
                "id": f"watchlist-earnings-{index + 1}",
                "title": f"{row.get('symbol', '')} \uc2e4\uc801 \uc608\uc815",
                "category": "earnings",
                "market": "watchlist",
                "date": row.get("reportDate", ""),
                "time": "\uc608\uc815",
                "summary": f"{row.get('name', row.get('symbol', ''))} \uc2e4\uc801 \ubc1c\ud45c \uc608\uc815\uc785\ub2c8\ub2e4.",
                "source": "Alpha Vantage",
                "symbol": row.get("symbol", ""),
                "url": "",
                "tone": "neutral",
                "sourceRefIds": [ref["id"]],
            })
        return events

    def _build_watchlist_news_events(self, news_items):
        events = []
        for index, article in enumerate(news_items[:4]):
            symbol = article.get("tickers", [""])[0] if article.get("tickers") else ""
            events.append({
                "id": f"watchlist-news-{index + 1}",
                "title": article.get("title", ""),
                "category": "news",
                "market": "watchlist",
                "date": article.get("publishedAt", "")[:10],
                "time": article.get("publishedAt", "")[11:16] or "\ubbf8\uc815",
                "summary": article.get("summary", ""),
                "source": article.get("source", "Alpha Vantage"),
                "symbol": symbol,
                "url": article.get("url", ""),
                "tone": self._tone_from_sentiment_label(article.get("sentimentLabel", "")),
                "sourceRefIds": article.get("sourceRefIds", []),
            })
        return events

    def _build_ipo_events(self, rows, source_refs):
        events = []
        for index, row in enumerate(rows[:8]):
            ref = build_source_ref(
                title=f"{row['symbol']} IPO calendar",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=row.get("ipoDate", ""),
                source_key="alpha_vantage::IPO_CALENDAR",
                symbol=row.get("symbol", ""),
            )
            source_refs.append(ref)
            low = row.get("priceRangeLow", 0.0)
            high = row.get("priceRangeHigh", 0.0)
            detail = f"\uacf5\ubaa8\uac00 \ubc94\uc704 {low:.2f}~{high:.2f} {row.get('currency', '')}" if (low or high) else "\uacf5\ubaa8\uac00 \ubc94\uc704 \ubbf8\uc815"
            events.append({
                "id": f"ipo-event-{index + 1}",
                "title": f"{row.get('name', row.get('symbol', ''))} IPO",
                "category": "ipo",
                "market": "global",
                "date": row.get("ipoDate", ""),
                "time": row.get("exchange", "\ubbf8\uc815"),
                "summary": detail,
                "source": "Alpha Vantage",
                "symbol": row.get("symbol", ""),
                "url": "",
                "tone": "neutral",
                "sourceRefIds": [ref["id"]],
            })
        return events

    def _build_domestic_calendar_events(self, disclosures, source_refs):
        events = []
        for index, disclosure in enumerate(disclosures[:8]):
            ref = build_source_ref(
                title=disclosure.get("reportName", "\uad6d\ub0b4 \uacf5\uc2dc"),
                kind="disclosure",
                publisher="OpenDART",
                published_at=disclosure.get("receiptDate", ""),
                source_key="opendart::list",
                url=disclosure.get("url", ""),
                symbol=disclosure.get("stockCode", ""),
            )
            source_refs.append(ref)
            events.append({
                "id": f"domestic-calendar-{index + 1}",
                "title": disclosure.get("corpName", "\uad6d\ub0b4 \uacf5\uc2dc"),
                "category": "disclosure",
                "market": "domestic",
                "date": self._to_date(disclosure.get("receiptDate", "")),
                "time": "\uacf5\uc2dc",
                "summary": disclosure.get("reportName", ""),
                "source": "OpenDART",
                "symbol": disclosure.get("stockCode", ""),
                "url": disclosure.get("url", ""),
                "tone": "neutral",
                "sourceRefIds": [ref["id"]],
            })
        return events

    def _build_calendar_highlights(self, *, watchlist_events, market_events, domestic_events, treasury, source_refs):
        items = []
        if watchlist_events:
            items.append({
                "label": "\uad00\uc2ec\uc885\ubaa9 \uc2e4\uc801",
                "value": f"{len(watchlist_events)}\uac74",
                "detail": watchlist_events[0]["title"],
                "tone": "positive" if len(watchlist_events) >= 2 else "neutral",
                "sourceRefIds": watchlist_events[0].get("sourceRefIds", []),
            })
        if market_events:
            items.append({
                "label": "IPO \uce98\ub9b0\ub354",
                "value": f"{len(market_events)}\uac74",
                "detail": market_events[0]["title"],
                "tone": "neutral",
                "sourceRefIds": market_events[0].get("sourceRefIds", []),
            })
        if treasury:
            ref = build_source_ref(
                title="\ubbf8\uad6d 10\ub144\ubb3c \uad6d\ucc44 \uc218\uc775\ub960",
                kind="economic",
                publisher="Alpha Vantage",
                published_at=treasury.get("date", ""),
                source_key="alpha_vantage::TREASURY_YIELD",
            )
            source_refs.append(ref)
            items.append({
                "label": "\ubbf8\uad6d 10\ub144\ubb3c",
                "value": f"{treasury.get('value', 0):.2f}%",
                "detail": f"\uc804\uc77c \ub300\ube44 {treasury.get('changePercent', 0):+.2f}%p",
                "tone": "negative" if treasury.get("changePercent", 0) > 0 else "positive",
                "sourceRefIds": [ref["id"]],
            })
        if domestic_events:
            items.append({
                "label": "\uad6d\ub0b4 \uacf5\uc2dc",
                "value": f"{len(domestic_events)}\uac74",
                "detail": domestic_events[0]["title"],
                "tone": "neutral",
                "sourceRefIds": domestic_events[0].get("sourceRefIds", []),
            })
        return items[:4]

    def _build_calendar_summary(self, watchlist_events, market_events, domestic_events, treasury) -> str:
        watchlist = f"\uad00\uc2ec\uc885\ubaa9 \uc2e4\uc801\uc740 {watchlist_events[0]['title']}\ubd80\ud130 \uccb4\ud06c" if watchlist_events else "\uad00\uc2ec\uc885\ubaa9 \uc2e4\uc801 \uc77c\uc815\uc740 \uc544\uc9c1 \ubd80\uc871\ud569\ub2c8\ub2e4"
        market = f"IPO\ub294 {market_events[0]['title']}\uac00 \uac00\uc7a5 \uac00\uae5d\uc2b5\ub2c8\ub2e4" if market_events else "IPO \uc77c\uc815\uc740 \uc544\uc9c1 \ubd80\uc871\ud569\ub2c8\ub2e4"
        domestic = f"\uad6d\ub0b4 \uacf5\uc2dc\ub294 {domestic_events[0]['title']} \uad00\ub828 \uacf5\uc2dc\ub97c \uc6b0\uc120 \ud655\uc778" if domestic_events else "OpenDART \uc5f0\ub3d9 \ub610\ub294 \ucd5c\uc2e0 \uacf5\uc2dc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4"
        macro = f"10\ub144\ubb3c \uae08\ub9ac\ub294 {treasury.get('value', 0):.2f}% \uc218\uc900" if treasury else "\ub9e4\ud06c\ub85c \uae08\ub9ac \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4"
        return f"{watchlist}. {market}. {domestic}. {macro}."

    def _merge_ref_ids(self, *groups) -> list[str]:
        merged = []
        for group in groups:
            for item in group[:3]:
                merged.extend(item.get("sourceRefIds", []))
        return list(dict.fromkeys(merged))

    def _to_date(self, value: str) -> str:
        if value and len(value) == 8 and value.isdigit():
            return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
        return value[:10]

    def _to_iso(self, value: str) -> str:
        date_only = self._to_date(value)
        return f"{date_only}T00:00:00+00:00" if date_only else datetime.now(timezone.utc).isoformat()
