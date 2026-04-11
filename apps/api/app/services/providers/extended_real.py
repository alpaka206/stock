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
        featured = featured_news[0]["title"] if featured_news else "해외 헤드라인이 아직 부족합니다"
        watchlist = watchlist_news[0]["title"] if watchlist_news else "관심종목 뉴스가 아직 적습니다"
        domestic = domestic_disclosures[0]["headline"] if domestic_disclosures else "OpenDART 연동 또는 최신 공시가 없습니다"
        return f"해외 메인 헤드라인은 '{featured}' 중심으로 움직이고, 관심종목 흐름은 '{watchlist}'를 우선 확인할 구간입니다. 국내는 '{domestic}' 공시를 함께 봐야 합니다."

    def _build_news_drivers(self, featured_news, watchlist_news, domestic_disclosures):
        items = []
        if featured_news:
            items.append({
                "text": f"해외 헤드라인은 {featured_news[0]['source']} 발 {featured_news[0]['title']}를 우선 확인합니다.",
                "sourceRefIds": featured_news[0].get("sourceRefIds", []),
            })
        if watchlist_news:
            symbol = watchlist_news[0].get("tickers", [""])[0] if watchlist_news[0].get("tickers") else "핵심 심볼"
            items.append({
                "text": f"관심종목은 {symbol} 관련 뉴스 반응이 가장 빠릅니다.",
                "sourceRefIds": watchlist_news[0].get("sourceRefIds", []),
            })
        if domestic_disclosures:
            items.append({
                "text": f"국내는 {domestic_disclosures[0]['headline']} 공시를 체크 포인트로 둡니다.",
                "sourceRefIds": domestic_disclosures[0].get("sourceRefIds", []),
            })
        return items or [{"text": "현재 연결된 뉴스/공시 데이터가 충분하지 않습니다.", "sourceRefIds": []}]

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
                title=disclosure.get("reportName", "국내 공시"),
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
                "headline": disclosure.get("corpName", "국내 공시"),
                "source": "OpenDART",
                "summary": disclosure.get("reportName", ""),
                "impact": "공시",
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
                "title": f"{row.get('symbol', '')} 실적 예정",
                "category": "earnings",
                "market": "watchlist",
                "date": row.get("reportDate", ""),
                "time": "예정",
                "summary": f"{row.get('name', row.get('symbol', ''))} 실적 발표 예정입니다.",
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
                "time": article.get("publishedAt", "")[11:16] or "미정",
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
            detail = f"공모가 범위 {low:.2f}~{high:.2f} {row.get('currency', '')}" if (low or high) else "공모가 범위 미정"
            events.append({
                "id": f"ipo-event-{index + 1}",
                "title": f"{row.get('name', row.get('symbol', ''))} IPO",
                "category": "ipo",
                "market": "global",
                "date": row.get("ipoDate", ""),
                "time": row.get("exchange", "미정"),
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
                title=disclosure.get("reportName", "국내 공시"),
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
                "title": disclosure.get("corpName", "국내 공시"),
                "category": "disclosure",
                "market": "domestic",
                "date": self._to_date(disclosure.get("receiptDate", "")),
                "time": "공시",
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
                "label": "관심종목 실적",
                "value": f"{len(watchlist_events)}건",
                "detail": watchlist_events[0]["title"],
                "tone": "positive" if len(watchlist_events) >= 2 else "neutral",
                "sourceRefIds": watchlist_events[0].get("sourceRefIds", []),
            })
        if market_events:
            items.append({
                "label": "IPO 캘린더",
                "value": f"{len(market_events)}건",
                "detail": market_events[0]["title"],
                "tone": "neutral",
                "sourceRefIds": market_events[0].get("sourceRefIds", []),
            })
        if treasury:
            ref = build_source_ref(
                title="미국 10년물 국채 수익률",
                kind="economic",
                publisher="Alpha Vantage",
                published_at=treasury.get("date", ""),
                source_key="alpha_vantage::TREASURY_YIELD",
            )
            source_refs.append(ref)
            items.append({
                "label": "미국 10년물",
                "value": f"{treasury.get('value', 0):.2f}%",
                "detail": f"전일 대비 {treasury.get('changePercent', 0):+.2f}%p",
                "tone": "negative" if treasury.get("changePercent", 0) > 0 else "positive",
                "sourceRefIds": [ref["id"]],
            })
        if domestic_events:
            items.append({
                "label": "국내 공시",
                "value": f"{len(domestic_events)}건",
                "detail": domestic_events[0]["title"],
                "tone": "neutral",
                "sourceRefIds": domestic_events[0].get("sourceRefIds", []),
            })
        return items[:4]

    def _build_calendar_summary(self, watchlist_events, market_events, domestic_events, treasury) -> str:
        watchlist = f"관심종목 실적은 {watchlist_events[0]['title']}부터 체크" if watchlist_events else "관심종목 실적 일정은 아직 부족합니다"
        market = f"IPO는 {market_events[0]['title']}가 가장 가깝습니다" if market_events else "IPO 일정은 아직 부족합니다"
        domestic = f"국내 공시는 {domestic_events[0]['title']} 관련 공시를 우선 확인" if domestic_events else "OpenDART 연동 또는 최신 공시가 없습니다"
        macro = f"10년물 금리는 {treasury.get('value', 0):.2f}% 수준" if treasury else "매크로 금리 데이터가 없습니다"
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
