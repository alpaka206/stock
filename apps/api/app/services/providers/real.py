from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar

from app.config import Settings
from app.services.clients.alpha_vantage import AlphaVantageClient
from app.services.clients.google_news import GoogleNewsClient
from app.services.clients.yahoo_market import YahooMarketClient
from app.services.clients.summary_router import ResearchSummaryClient
from app.services.deterministic_summary import build_deterministic_page_summary
from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptBundle
from app.services.providers.base import ResearchProvider
from app.services.providers.history_builders import (
    build_history_event_markers,
    build_history_event_timeline,
    build_history_move_reasons,
    build_history_overlaps,
    fallback_history_summary,
    history_available_ranges,
    history_range_label,
    slice_history_series,
)
from app.services.providers.radar_builders import (
    RadarRawRow,
    build_radar_alert_rules,
    build_radar_broker_reports,
    build_radar_detected_alerts,
    build_radar_folder_tree,
    build_radar_key_issues,
    build_radar_schedule,
    build_radar_sector_cards,
    build_radar_top_picks,
    build_radar_watchlist_rows,
)
from app.services.providers.stock_builders import (
    build_price_series,
    build_related_symbols,
    build_stock_chart_overlays,
    build_stock_event_markers,
    build_stock_indicator_guides,
    build_stock_instrument,
    build_stock_issue_cards,
    build_stock_pattern_cards,
    build_stock_rule_preset_definitions,
    build_stock_score_summary,
    build_stock_technical_metrics,
    fallback_stock_thesis,
)
from app.services.research_metrics import (
    compute_stock_score,
    compute_watchlist_score,
    identify_turning_points,
    percent_change,
    simple_return,
    volume_ratio,
)
from app.services.source_refs import (
    build_missing_data,
    build_source_ref,
    collect_source_ref_ids,
    dedupe_source_refs,
)

FetchResultT = TypeVar("FetchResultT")
FAST_FETCH_TIMEOUT_SECONDS = 4.0
SUMMARY_TIMEOUT_SECONDS = 6.0


class RealResearchProvider(ResearchProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.market_data = AlphaVantageClient(
            api_key=settings.alpha_vantage_api_key,
            base_url=settings.alpha_vantage_base_url,
            timeout_seconds=settings.request_timeout_seconds,
            cache_ttl_seconds=settings.provider_cache_ttl_seconds,
        )
        self.yahoo_market = YahooMarketClient(
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.google_news = GoogleNewsClient(
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.llm = ResearchSummaryClient(
            llm_provider=settings.llm_provider,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
            gemini_base_url=settings.gemini_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )

    async def search_instruments(
        self, *, query: str, limit: int = 6
    ) -> list[dict[str, Any]]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        items = await self.yahoo_market.search_instruments(normalized_query, limit=limit)
        if items:
            return items[:limit]

        if normalized_query.isdigit() and len(normalized_query) == 6:
            fallback_items: list[dict[str, Any]] = []
            for suffix, exchange in ((".KS", "KRX"), (".KQ", "KOSDAQ")):
                candidate_symbol = f"{normalized_query}{suffix}"
                try:
                    overview = await self.yahoo_market.get_company_overview(candidate_symbol)
                except ExternalServiceError:
                    continue

                fallback_items.append(
                    {
                        "symbol": candidate_symbol,
                        "name": overview.get("name", candidate_symbol),
                        "securityCode": normalized_query,
                        "aliases": [overview.get("name", candidate_symbol)],
                        "sector": overview.get("sector", "미분류"),
                        "exchange": overview.get("exchange", exchange) or exchange,
                    }
                )

            deduped: list[dict[str, Any]] = []
            seen_symbols: set[str] = set()
            for item in fallback_items:
                symbol = str(item.get("symbol", "")).upper()
                if not symbol or symbol in seen_symbols:
                    continue
                seen_symbols.add(symbol)
                deduped.append(item)

            return deduped[:limit]

        return []

    async def get_overview(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []

        benchmarks, sector_proxies, treasury, top_movers, news_items = await asyncio.gather(
            self._build_benchmark_cards(source_refs, missing_data),
            self._build_sector_proxy_cards(source_refs, missing_data),
            self._safe_fetch(
                field="overview.treasuryYield10Y",
                expected_source="Alpha Vantage TREASURY_YIELD",
                missing_data=missing_data,
                fetcher=self.market_data.get_treasury_yield,
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            self._safe_fetch(
                field="overview.topMovers",
                expected_source="Alpha Vantage TOP_GAINERS_LOSERS",
                missing_data=missing_data,
                fetcher=self.market_data.get_top_movers,
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            self._build_news_items(
                source_refs=source_refs,
                field="overview.news",
                expected_source="Alpha Vantage NEWS_SENTIMENT",
                missing_data=missing_data,
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
        )
        if treasury:
            treasury_ref = build_source_ref(
                title="미국 10년물 국채 수익률",
                kind="economic",
                publisher="Alpha Vantage",
                published_at=treasury["date"],
                source_key="alpha_vantage::TREASURY_YIELD",
            )
            source_refs.append(treasury_ref)
            treasury["sourceRefIds"] = [treasury_ref["id"]]

        if top_movers:
            movers_ref = build_source_ref(
                title="미국 증시 상위 상승·하락 종목",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=datetime.now(timezone.utc),
                source_key="alpha_vantage::TOP_GAINERS_LOSERS",
            )
            source_refs.append(movers_ref)
            for group_name in top_movers:
                for item in top_movers[group_name]:
                    item["sourceRefIds"] = [movers_ref["id"]]

        facts = {
            "benchmarks": benchmarks,
            "sectorProxies": sector_proxies,
            "treasuryYield10Y": treasury or {},
            "topMovers": top_movers or {},
            "notableNews": news_items,
        }
        benchmark_snapshot = self._build_overview_benchmark_snapshot(
            benchmarks=benchmarks,
            treasury=treasury,
        )
        payload = await self._summarize(
            page_key="overview",
            prompt_bundle=prompt_bundle,
            facts=facts,
            source_refs=source_refs,
            missing_data=missing_data,
        )
        payload["benchmarkSnapshot"] = benchmark_snapshot
        payload["sectorStrength"] = self._hydrate_overview_sector_strength(
            items=payload.get("sectorStrength"),
            sector_proxies=sector_proxies,
        )
        payload["notableNews"] = self._hydrate_overview_news(
            items=payload.get("notableNews"),
            news_items=news_items,
        )
        return self._finalize_payload(payload, source_refs, missing_data)

    async def get_radar(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        return await self._get_radar_v2(prompt_bundle=prompt_bundle)

    async def get_stock_detail(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        return await self._get_stock_detail_v2(symbol=symbol, prompt_bundle=prompt_bundle)

    async def get_history(
        self,
        *,
        symbol: str | None,
        range: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        prompt_bundle: PromptBundle,
    ) -> dict[str, Any]:
        return await self._get_history_v2(
            symbol=symbol,
            range=range,
            from_date=from_date,
            to_date=to_date,
            prompt_bundle=prompt_bundle,
        )

    async def _get_radar_v2(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []
        now = datetime.now(timezone.utc)

        sector_map_ref = build_source_ref(
            title="Radar 기본 섹터 맵",
            kind="internal_config",
            publisher="stock-workspace",
            published_at=now,
            source_key="settings::STOCK_RADAR_SECTORS",
        )
        source_refs.append(sector_map_ref)

        news_items, series_results = await asyncio.gather(
            self._build_news_items(
                source_refs=source_refs,
                field="radar.news",
                expected_source="Alpha Vantage NEWS_SENTIMENT",
                missing_data=missing_data,
                tickers=self.settings.radar_symbols,
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            asyncio.gather(
                *[
                    self._get_daily_series_with_backup(
                        field=f"radar.series.{symbol}",
                        symbol=symbol,
                        limit=60,
                        missing_data=missing_data,
                        soft_timeout_seconds=self._provider_soft_timeout_seconds(),
                    )
                    for symbol in self.settings.radar_symbols
                ]
            ),
        )
        news_by_symbol = self._group_news_by_symbol(news_items)

        raw_rows: list[RadarRawRow] = []
        for symbol, (series, series_publisher, series_source_key) in zip(
            self.settings.radar_symbols, series_results
        ):
            if not series or len(series) < 2:
                continue

            series_ref = build_source_ref(
                title=f"{symbol} 일별 시계열",
                kind="market_data",
                publisher=series_publisher,
                published_at=series[0]["date"],
                source_key=series_source_key,
                symbol=symbol,
            )
            source_refs.append(series_ref)
            sentiment_score = self._average_sentiment(news_by_symbol.get(symbol, []))
            score = compute_watchlist_score(series, sentiment_score)
            raw_rows.append(
                {
                    "symbol": symbol,
                    "sector": self.settings.radar_sector_map.get(symbol, "미분류"),
                    "price": round(series[0]["close"], 2),
                    "changePercent": percent_change(series[0]["close"], series[1]["close"]),
                    "return20d": simple_return(series, 20),
                    "volumeRatio": volume_ratio(series),
                    "sentimentScore": round(sentiment_score, 2),
                    "score": score,
                    "condition": self._watchlist_condition(score),
                    "sourceRefIds": [series_ref["id"], sector_map_ref["id"]],
                }
            )

        if not raw_rows:
            raise ExternalServiceError("radar 화면을 구성할 watchlist 데이터를 만들지 못했습니다.")

        watchlist_rows = build_radar_watchlist_rows(
            raw_rows,
            news_by_symbol,
            instrument_name=self._instrument_name,
            security_code=self._security_code,
            folder_id=self._radar_folder_id,
            tags=self._radar_tags,
            next_event=self._radar_next_event,
            relative_strength_score=self._relative_strength_score,
        )
        sector_cards = build_radar_sector_cards(
            watchlist_rows,
            sector_catalyst=self._radar_sector_catalyst,
        )
        broker_reports = build_radar_broker_reports(sector_cards)
        key_schedule = build_radar_schedule(sector_cards)
        key_issues = build_radar_key_issues(
            news_items,
            sector_by_symbol=self.settings.radar_sector_map,
            impact_from_sentiment=self._impact_from_sentiment,
        )
        top_picks = build_radar_top_picks(sector_cards)
        folder_tree = build_radar_folder_tree(watchlist_rows, slugify=self._slugify)
        alert_rules = build_radar_alert_rules()
        detected_alerts = build_radar_detected_alerts(watchlist_rows)

        payload = await self._summarize(
            page_key="radar",
            prompt_bundle=prompt_bundle,
            facts={
                "selectedSector": sector_cards[0]["sector"] if sector_cards else "",
                "watchlistRows": watchlist_rows,
                "sectorCards": sector_cards,
                "keyIssues": key_issues,
                "topPicks": top_picks,
                "detectedAlerts": detected_alerts,
            },
            source_refs=source_refs,
            missing_data=missing_data,
        )
        if not payload.get("selectedSectorSummary"):
            payload["selectedSectorSummary"] = {
                "text": self._fallback_radar_sector_summary(sector_cards[0] if sector_cards else None),
                "sourceRefIds": sector_cards[0]["sourceRefIds"] if sector_cards else [],
            }
        payload["folderTree"] = folder_tree
        payload["watchlistRows"] = watchlist_rows
        payload["sectorCards"] = sector_cards
        payload["brokerReports"] = broker_reports
        payload["keySchedule"] = key_schedule
        payload["keyIssues"] = key_issues
        payload["topPicks"] = top_picks
        payload["alertRules"] = alert_rules
        payload["detectedAlerts"] = detected_alerts
        return self._finalize_payload(payload, source_refs, missing_data)

    async def _get_stock_detail_v2(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []

        (
            (series, series_publisher, series_source_key),
            (overview, overview_publisher, overview_source_key),
            news_items,
        ) = await asyncio.gather(
            self._get_daily_series_with_backup(
                field=f"stocks.series.{symbol}",
                symbol=symbol,
                limit=140,
                missing_data=missing_data,
                soft_timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            self._get_company_overview_with_backup(
                field=f"stocks.overview.{symbol}",
                symbol=symbol,
                missing_data=missing_data,
                soft_timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            self._build_news_items(
                source_refs=source_refs,
                field=f"stocks.news.{symbol}",
                expected_source="Alpha Vantage NEWS_SENTIMENT",
                missing_data=missing_data,
                tickers=[symbol],
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
        )
        if not series or len(series) < 2 or not overview:
            raise ExternalServiceError(f"{symbol} 상세 분석에 필요한 데이터를 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{symbol} 일별 시계열",
            kind="market_data",
            publisher=series_publisher,
            published_at=series[0]["date"],
            source_key=series_source_key,
            symbol=symbol,
        )
        overview_ref = build_source_ref(
            title=f"{symbol} 기업 개요",
            kind="fundamentals",
            publisher=overview_publisher,
            published_at=datetime.now(timezone.utc),
            source_key=overview_source_key,
            symbol=symbol,
        )
        source_refs.extend([series_ref, overview_ref])

        score_model = compute_stock_score(series, self._average_sentiment(news_items))
        price_series = build_price_series(series, limit=60)
        event_markers = build_stock_event_markers(
            symbol,
            news_items,
            tone_from_sentiment_label=self._tone_from_sentiment_label,
        )
        indicator_guides = build_stock_indicator_guides(series)
        chart_overlays = build_stock_chart_overlays(series, limit=60)
        technical_metrics = build_stock_technical_metrics(series, series_ref["id"])
        pattern_cards = build_stock_pattern_cards(series, series_ref["id"])
        rule_preset_definitions = build_stock_rule_preset_definitions()
        score_summary = build_stock_score_summary(score_model)
        issue_cards = build_stock_issue_cards(
            symbol,
            overview,
            news_items,
            sector_by_symbol=self.settings.radar_sector_map,
            tone_from_sentiment_label=self._tone_from_sentiment_label,
        )
        related_symbols = build_related_symbols(
            symbol,
            overview.get("sector", ""),
            radar_symbols=self.settings.radar_symbols,
            sector_by_symbol=self.settings.radar_sector_map,
        )

        payload = await self._summarize(
            page_key="stocks",
            prompt_bundle=prompt_bundle,
            facts={
                "symbol": symbol,
                "company": overview,
                "latestPrice": round(series[0]["close"], 2),
                "changePercent": percent_change(series[0]["close"], series[1]["close"]),
                "scoreSummary": score_summary,
                "issueCards": issue_cards,
                "indicatorGuides": indicator_guides,
                "technicalMetrics": technical_metrics,
                "patternCards": pattern_cards,
                "relatedSymbols": related_symbols,
            },
            source_refs=source_refs,
            missing_data=missing_data,
        )
        payload["instrument"] = build_stock_instrument(
            symbol,
            overview,
            security_code=self._security_code,
            format_market_cap=self._format_market_cap,
        )
        payload["latestPrice"] = round(series[0]["close"], 2)
        payload["changePercent"] = percent_change(series[0]["close"], series[1]["close"])
        payload["thesis"] = payload.get("thesis") or fallback_stock_thesis(
            symbol=symbol,
            overview=overview,
            news_items=news_items,
        )
        payload["priceSeries"] = price_series
        payload["eventMarkers"] = event_markers
        payload["indicatorGuides"] = indicator_guides
        payload["chartOverlays"] = chart_overlays
        payload["technicalMetrics"] = technical_metrics
        payload["patternCards"] = pattern_cards
        payload["rulePresetDefinitions"] = rule_preset_definitions
        payload["scoreSummary"] = score_summary
        payload["flowMetrics"] = []
        payload["flowUnavailable"] = {
            "label": "수급 데이터 준비 중",
            "reason": "무료 범위에서 기관/개인/외국인 수급 source가 아직 연결되지 않았습니다.",
            "expectedSource": "flow provider",
        }
        payload["optionsShortMetrics"] = []
        payload["optionsUnavailable"] = {
            "label": "공매도/옵션 데이터 준비 중",
            "reason": "실제 옵션/공매도 비율 source를 아직 연결하지 않았습니다.",
            "expectedSource": "options-short provider",
        }
        payload["issueCards"] = issue_cards
        payload["relatedSymbols"] = related_symbols
        return self._finalize_payload(payload, source_refs, missing_data)

    async def _get_history_v2(
        self,
        *,
        symbol: str | None,
        range: str | None,
        from_date: str | None,
        to_date: str | None,
        prompt_bundle: PromptBundle,
    ) -> dict[str, Any]:
        target_symbol = symbol or self.settings.radar_symbols[0]
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = [
            build_missing_data(
                "history.lookback",
                "무료 Alpha Vantage 시계열은 compact 범위 중심으로 제공합니다.",
                "Alpha Vantage premium 또는 별도 history provider",
            )
        ]

        (series, series_publisher, series_source_key), news_items = await asyncio.gather(
            self._get_daily_series_with_backup(
                field=f"history.series.{target_symbol}",
                symbol=target_symbol,
                limit=100,
                missing_data=missing_data,
                soft_timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
            self._build_news_items(
                source_refs=source_refs,
                field=f"history.news.{target_symbol}",
                expected_source="Alpha Vantage NEWS_SENTIMENT",
                missing_data=missing_data,
                tickers=[target_symbol],
                timeout_seconds=self._provider_soft_timeout_seconds(),
            ),
        )
        if not series or len(series) < 2:
            raise ExternalServiceError(f"{target_symbol} 히스토리 시계열을 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{target_symbol} 히스토리 일별 시계열",
            kind="market_data",
            publisher=series_publisher,
            published_at=series[0]["date"],
            source_key=series_source_key,
            symbol=target_symbol,
        )
        source_refs.append(series_ref)

        filtered_series = slice_history_series(
            series=series,
            range_value=range,
            from_date=from_date,
            to_date=to_date,
        )
        price_series = build_price_series(filtered_series, limit=len(filtered_series))
        turning_points = identify_turning_points(filtered_series, limit=4)
        event_timeline = build_history_event_timeline(
            symbol=target_symbol,
            news_items=news_items,
            turning_points=turning_points,
            filtered_series=filtered_series,
            tone_from_sentiment_label=self._tone_from_sentiment_label,
        )
        move_reasons = build_history_move_reasons(turning_points, series_ref["id"])
        overlapping_indicators = build_history_overlaps(
            filtered_series, turning_points, series_ref["id"]
        )
        event_markers = build_history_event_markers(event_timeline)

        payload = await self._summarize(
            page_key="history",
            prompt_bundle=prompt_bundle,
            facts={
                "symbol": target_symbol,
                "eventTimeline": event_timeline,
                "moveReasons": move_reasons,
                "overlappingIndicators": overlapping_indicators,
            },
            source_refs=source_refs,
            missing_data=missing_data,
        )
        payload["symbol"] = target_symbol
        payload["rangeLabel"] = history_range_label(
            price_series=price_series,
            from_date=from_date,
            to_date=to_date,
        )
        payload["availableRanges"] = history_available_ranges()
        payload["priceSeries"] = price_series
        payload["eventMarkers"] = event_markers
        payload["eventTimeline"] = event_timeline
        payload["moveSummary"] = payload.get("moveSummary") or {
            "text": fallback_history_summary(move_reasons),
            "sourceRefIds": [series_ref["id"]],
        }
        payload["moveReasons"] = move_reasons
        payload["overlappingIndicators"] = overlapping_indicators
        payload["analogsOrPatterns"] = payload.get("analogsOrPatterns") or [
            {
                "text": "실적 이후 거래량 동반 추세 강화 패턴",
                "sourceRefIds": [series_ref["id"]],
            }
        ]
        return self._finalize_payload(payload, source_refs, missing_data)

    def _fallback_radar_sector_summary(self, sector_card: dict[str, Any] | None) -> str:
        if not sector_card:
            return "선택 섹터 요약을 만들기 위한 데이터가 아직 충분하지 않습니다."
        return (
            f"{sector_card['sector']} 섹터에서 {sector_card['topPick']}가 가장 앞서며, "
            f"{sector_card['catalyst']}를 핵심 촉매로 봅니다."
        )

    def _instrument_name(self, symbol: str) -> str:
        names = {
            "NVDA": "NVIDIA",
            "AMD": "AMD",
            "AVGO": "Broadcom",
            "MSFT": "Microsoft",
            "CRWD": "CrowdStrike",
            "VRT": "Vertiv",
        }
        return names.get(symbol, symbol)

    def _security_code(self, symbol: str) -> str:
        codes = {
            "NVDA": "NV-001",
            "AMD": "AM-004",
            "AVGO": "AV-002",
            "MSFT": "MS-008",
            "CRWD": "CR-007",
            "VRT": "VR-003",
        }
        return codes.get(symbol, f"{symbol}-000")

    def _radar_folder_id(self, sector: str, score: float) -> str:
        if sector in {"반도체", "전력 인프라"}:
            return "ai-infra"
        if score >= 80:
            return "high-conviction"
        return "all"

    def _radar_tags(self, sector: str, score: float) -> list[str]:
        tags = [sector]
        if score >= 80:
            tags.append("리더")
        if sector == "전력 인프라":
            tags.append("병목")
        if sector == "반도체":
            tags.append("AI")
        return tags

    def _radar_next_event(self, sector: str) -> str:
        if sector == "반도체":
            return "실적 / 제품 이벤트"
        if sector == "전력 인프라":
            return "수주 / 설비 메모"
        return "뉴스 체크"

    def _radar_sector_catalyst(self, sector: str) -> str:
        if sector == "반도체":
            return "실적 가시성과 AI 투자 확대"
        if sector == "전력 인프라":
            return "전력 병목과 냉각 인프라 수요"
        if sector == "사이버보안":
            return "방어적 성장과 계약 갱신"
        return "섹터 뉴스 흐름"

    def _relative_strength_score(self, row: dict[str, Any]) -> float:
        return round(
            max(0.0, min(100.0, 60 + row.get("return20d", 0.0) * 1.8 + row.get("sentimentScore", 0.0) * 10)),
            1,
        )

    def _impact_from_sentiment(self, value: str) -> str:
        normalized = value.lower()
        if "bullish" in normalized or "positive" in normalized:
            return "긍정"
        if "bearish" in normalized or "negative" in normalized:
            return "부정"
        return "중립"

    def _tone_from_sentiment_label(self, value: str) -> str:
        impact = self._impact_from_sentiment(value)
        if impact == "긍정":
            return "positive"
        if impact == "부정":
            return "negative"
        return "neutral"

    def _format_market_cap(self, value: float) -> str:
        if value >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f}T"
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.0f}B"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.0f}M"
        return f"{value:.0f}"

    def _slugify(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("/", "-")

    async def _summarize(
        self,
        *,
        page_key: str,
        prompt_bundle: PromptBundle,
        facts: dict[str, Any],
        source_refs: list[dict[str, Any]],
        missing_data: list[dict[str, str]],
    ) -> dict[str, Any]:
        if not source_refs:
            raise ExternalServiceError(f"{page_key} summary cannot proceed without sourceRefs.")
        deduped_source_refs = dedupe_source_refs(source_refs)
        try:
            return await asyncio.wait_for(
                self.llm.generate_page_response(
                    prompt_bundle=prompt_bundle,
                    page_key=page_key,
                    facts=facts,
                    source_refs=deduped_source_refs,
                    missing_data=missing_data,
                ),
                timeout=self._summary_timeout_seconds(),
            )
        except asyncio.TimeoutError:
            return build_deterministic_page_summary(
                page_key=page_key,
                facts=facts,
                missing_data=missing_data,
                fallback_reason="summary generation timed out",
            )
        except (ProviderConfigurationError, ExternalServiceError) as exc:
            return build_deterministic_page_summary(
                page_key=page_key,
                facts=facts,
                missing_data=missing_data,
                fallback_reason=str(exc),
            )

    async def _build_benchmark_cards(
        self, source_refs: list[dict[str, Any]], missing_data: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        cards: list[dict[str, Any]] = []
        entries = list(self.settings.overview_benchmarks.items())
        results = await asyncio.gather(
            *[
                self._get_daily_series_with_backup(
                    field=f"overview.benchmark.{symbol}",
                    symbol=symbol,
                    limit=30,
                    missing_data=missing_data,
                    soft_timeout_seconds=self._provider_soft_timeout_seconds(),
                )
                for symbol, _label in entries
            ]
        )
        for (symbol, label), (series, series_publisher, series_source_key) in zip(entries, results):
            if not series or len(series) < 2:
                continue
            ref = build_source_ref(
                title=f"{label} 일별 시계열",
                kind="market_data",
                publisher=series_publisher,
                published_at=series[0]["date"],
                source_key=series_source_key,
                symbol=symbol,
            )
            source_refs.append(ref)
            cards.append(
                {
                    "symbol": symbol,
                    "label": label,
                    "price": round(series[0]["close"], 2),
                    "changePercent": percent_change(series[0]["close"], series[1]["close"]),
                    "return5d": simple_return(series, 5),
                    "return20d": simple_return(series, 20),
                    "volumeRatio": volume_ratio(series),
                    "sourceRefIds": [ref["id"]],
                }
            )
        return cards

    async def _build_sector_proxy_cards(
        self, source_refs: list[dict[str, Any]], missing_data: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        proxies: list[dict[str, Any]] = []
        entries = list(self.settings.sector_proxies.items())
        results = await asyncio.gather(
            *[
                self._get_daily_series_with_backup(
                    field=f"overview.sectorProxy.{symbol}",
                    symbol=symbol,
                    limit=30,
                    missing_data=missing_data,
                    soft_timeout_seconds=self._provider_soft_timeout_seconds(),
                )
                for symbol, _label in entries
            ]
        )
        for (symbol, label), (series, series_publisher, series_source_key) in zip(entries, results):
            if not series or len(series) < 2:
                continue
            ref = build_source_ref(
                title=f"{label} ETF 일별 시계열",
                kind="market_data",
                publisher=series_publisher,
                published_at=series[0]["date"],
                source_key=series_source_key,
                symbol=symbol,
            )
            source_refs.append(ref)
            proxies.append(
                {
                    "symbol": symbol,
                    "label": label,
                    "changePercent": percent_change(series[0]["close"], series[1]["close"]),
                    "return20d": simple_return(series, 20),
                    "volumeRatio": volume_ratio(series),
                    "sourceRefIds": [ref["id"]],
                }
            )
        return proxies

    def _build_overview_benchmark_snapshot(
        self,
        *,
        benchmarks: list[dict[str, Any]],
        treasury: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        snapshot = [
            {
                "label": benchmark["label"],
                "symbol": benchmark["symbol"],
                "category": "시장 프록시",
                "value": benchmark["price"],
                "changePercent": benchmark["changePercent"],
                "note": f'{benchmark["label"]} 프록시 ETF 기준 흐름입니다.',
                "sourceRefIds": benchmark["sourceRefIds"],
            }
            for benchmark in benchmarks
        ]

        if treasury:
            snapshot.append(
                {
                    "label": "미국 10년물 금리",
                    "symbol": "US10Y",
                    "category": "금리",
                    "value": treasury["value"],
                    "changePercent": treasury["changePercent"],
                    "note": "장기 금리 민감도를 보는 기준 값입니다.",
                    "sourceRefIds": treasury["sourceRefIds"],
                }
            )

        return snapshot

    def _hydrate_overview_sector_strength(
        self,
        *,
        items: Any,
        sector_proxies: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not isinstance(items, list):
            return []

        change_by_label = {
            str(proxy.get("label", "")).strip().lower(): round(float(proxy["changePercent"]), 2)
            for proxy in sector_proxies
            if proxy.get("label") and "changePercent" in proxy
        }
        change_by_ref_id: dict[str, float] = {}
        for proxy in sector_proxies:
            if "changePercent" not in proxy:
                continue
            for ref_id in proxy.get("sourceRefIds", []):
                change_by_ref_id[str(ref_id)] = round(float(proxy["changePercent"]), 2)

        hydrated: list[dict[str, Any]] = []
        for raw_item in items:
            if not isinstance(raw_item, dict):
                continue

            item = {key: value for key, value in raw_item.items() if key != "changePercent"}
            change_percent = self._resolve_sector_change_percent(
                item=item,
                change_by_label=change_by_label,
                change_by_ref_id=change_by_ref_id,
            )
            if change_percent is not None:
                item["changePercent"] = change_percent
            hydrated.append(item)

        return hydrated

    def _resolve_sector_change_percent(
        self,
        *,
        item: dict[str, Any],
        change_by_label: dict[str, float],
        change_by_ref_id: dict[str, float],
    ) -> float | None:
        for ref_id in item.get("sourceRefIds", []):
            normalized_ref_id = str(ref_id)
            if normalized_ref_id in change_by_ref_id:
                return change_by_ref_id[normalized_ref_id]

        sector_name = str(item.get("sector", "")).strip().lower()
        if sector_name:
            return change_by_label.get(sector_name)

        return None

    def _hydrate_overview_news(
        self,
        *,
        items: Any,
        news_items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not isinstance(items, list):
            return []

        summary_by_ref_id: dict[str, str] = {}
        summary_by_headline: dict[str, str] = {}
        for article in news_items:
            summary = str(article.get("summary", "")).strip()
            if not summary:
                continue
            normalized_headline = str(article.get("title", "")).strip().lower()
            if normalized_headline:
                summary_by_headline[normalized_headline] = summary
            for ref_id in article.get("sourceRefIds", []):
                summary_by_ref_id[str(ref_id)] = summary

        hydrated: list[dict[str, Any]] = []
        for raw_item in items:
            if not isinstance(raw_item, dict):
                continue

            item = dict(raw_item)
            item["summary"] = self._resolve_news_summary(
                item=item,
                summary_by_ref_id=summary_by_ref_id,
                summary_by_headline=summary_by_headline,
            )
            hydrated.append(item)

        return hydrated

    def _resolve_news_summary(
        self,
        *,
        item: dict[str, Any],
        summary_by_ref_id: dict[str, str],
        summary_by_headline: dict[str, str],
    ) -> str:
        for ref_id in item.get("sourceRefIds", []):
            normalized_ref_id = str(ref_id)
            if normalized_ref_id in summary_by_ref_id:
                return summary_by_ref_id[normalized_ref_id]

        normalized_headline = str(item.get("headline", "")).strip().lower()
        if normalized_headline:
            return summary_by_headline.get(normalized_headline, "")

        return ""

    async def _build_news_items(
        self,
        *,
        source_refs: list[dict[str, Any]],
        field: str,
        expected_source: str,
        missing_data: list[dict[str, str]],
        tickers: list[str] | None = None,
        timeout_seconds: float | None = None,
    ) -> list[dict[str, Any]]:
        primary_missing_count = len(missing_data)
        articles = await self._safe_fetch(
            field=field,
            expected_source=expected_source,
            missing_data=missing_data,
            fetcher=self.market_data.get_news_sentiment,
            tickers=tickers,
            limit=8,
            timeout_seconds=timeout_seconds,
        )

        source_key = "alpha_vantage::NEWS_SENTIMENT"

        if not articles:
            fallback_articles = await self._safe_fetch(
                field=f"{field}.fallback",
                expected_source="Google News RSS search",
                missing_data=missing_data,
                fetcher=self._get_google_news_fallback,
                tickers=tickers,
                limit=8,
                timeout_seconds=timeout_seconds,
            )
            if fallback_articles:
                del missing_data[primary_missing_count:]
                articles = fallback_articles
                source_key = "google_news::rss_search"

        if not articles:
            return []

        hydrated: list[dict[str, Any]] = []
        for article in articles:
            ref = build_source_ref(
                title=article["title"],
                kind="news",
                publisher=article["source"] or "Google News RSS",
                published_at=article["publishedAt"],
                source_key=article.get("sourceKey", source_key),
                url=article["url"],
                symbol=",".join(article["tickers"]),
            )
            source_refs.append(ref)
            hydrated.append({**article, "sourceRefIds": [ref["id"]]})
        return hydrated

    async def _get_google_news_fallback(
        self, *, tickers: list[str] | None = None, limit: int = 8
    ) -> list[dict[str, Any]]:
        if tickers:
            return await self.google_news.get_watchlist_headlines(
                tickers=tickers,
                limit=limit,
            )
        return await self.google_news.get_market_headlines(limit=limit)

    async def _safe_fetch(
        self,
        *,
        field: str,
        expected_source: str,
        missing_data: list[dict[str, str]],
        fetcher: Callable[..., Awaitable[FetchResultT]],
        timeout_seconds: float | None = None,
        **kwargs: Any,
    ) -> FetchResultT | None:
        try:
            operation = fetcher(**kwargs)
            if timeout_seconds and timeout_seconds > 0:
                return await asyncio.wait_for(operation, timeout=timeout_seconds)
            return await operation
        except asyncio.TimeoutError:
            missing_data.append(
                build_missing_data(
                    field,
                    f"{expected_source} timed out after {timeout_seconds:.1f}s.",
                    expected_source,
                )
            )
            return None
        except ExternalServiceError as exc:
            missing_data.append(build_missing_data(field, str(exc), expected_source))
            return None

    async def _get_daily_series_with_backup(
        self,
        *,
        field: str,
        symbol: str,
        limit: int,
        missing_data: list[dict[str, str]],
        soft_timeout_seconds: float | None = None,
    ) -> tuple[list[dict[str, Any]] | None, str, str]:
        backup_series = await self._safe_fetch(
            field=field,
            expected_source="Yahoo Finance chart",
            missing_data=missing_data,
            fetcher=self.yahoo_market.get_daily_series,
            symbol=symbol,
            limit=limit,
            timeout_seconds=soft_timeout_seconds,
        )
        if backup_series and len(backup_series) >= 2:
            return backup_series, "Yahoo Finance", "yahoo_finance::chart"

        series = await self._safe_fetch(
            field=f"{field}.alpha",
            expected_source="Alpha Vantage TIME_SERIES_DAILY",
            missing_data=missing_data,
            fetcher=self.market_data.get_daily_series,
            symbol=symbol,
            limit=limit,
            timeout_seconds=soft_timeout_seconds,
        )
        if series and len(series) >= 2:
            return series, "Alpha Vantage", "alpha_vantage::TIME_SERIES_DAILY"

        return None, "Alpha Vantage", "alpha_vantage::TIME_SERIES_DAILY"

    async def _get_company_overview_with_backup(
        self,
        *,
        field: str,
        symbol: str,
        missing_data: list[dict[str, str]],
        soft_timeout_seconds: float | None = None,
    ) -> tuple[dict[str, Any] | None, str, str]:
        backup_overview = await self._safe_fetch(
            field=field,
            expected_source="Yahoo Finance search",
            missing_data=missing_data,
            fetcher=self.yahoo_market.get_company_overview,
            symbol=symbol,
            timeout_seconds=soft_timeout_seconds,
        )
        if backup_overview:
            if not backup_overview.get("marketCapitalization"):
                missing_data.append(
                    build_missing_data(
                        f"{field}.marketCap",
                        "Yahoo 공개 검색 백업은 시가총액을 제공하지 않습니다.",
                        "Yahoo Finance quote summary",
                    )
                )
            return backup_overview, "Yahoo Finance", "yahoo_finance::search"

        overview = await self._safe_fetch(
            field=f"{field}.alpha",
            expected_source="Alpha Vantage OVERVIEW",
            missing_data=missing_data,
            fetcher=self.market_data.get_company_overview,
            symbol=symbol,
            timeout_seconds=soft_timeout_seconds,
        )
        if overview:
            return overview, "Alpha Vantage", "alpha_vantage::OVERVIEW"

        return None, "Alpha Vantage", "alpha_vantage::OVERVIEW"

    def _provider_soft_timeout_seconds(self) -> float:
        return min(self.settings.request_timeout_seconds, FAST_FETCH_TIMEOUT_SECONDS)

    def _summary_timeout_seconds(self) -> float:
        return max(1.0, min(self.settings.request_timeout_seconds, SUMMARY_TIMEOUT_SECONDS))
    def _group_news_by_symbol(self, news_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in news_items:
            for symbol in item.get("tickers", []):
                grouped.setdefault(symbol, []).append(item)
        return grouped

    def _average_sentiment(self, news_items: list[dict[str, Any]]) -> float:
        if not news_items:
            return 0.0
        return round(
            sum(item.get("sentimentScore", 0.0) for item in news_items) / len(news_items),
            2,
        )

    def _watchlist_condition(self, score: float) -> str:
        if score >= 82:
            return "우선검토"
        if score >= 70:
            return "관심"
        if score >= 58:
            return "조건부 강세"
        return "리스크 확대"

    def _finalize_payload(
        self,
        payload: dict[str, Any],
        source_refs: list[dict[str, Any]],
        missing_data: list[dict[str, str]],
    ) -> dict[str, Any]:
        deduped_refs = dedupe_source_refs(source_refs)
        referenced_ids = collect_source_ref_ids(payload)
        filtered_refs = [
            ref for ref in deduped_refs if not referenced_ids or ref["id"] in referenced_ids
        ]
        payload["asOf"] = datetime.now(timezone.utc).isoformat()
        payload["sourceRefs"] = filtered_refs
        payload["missingData"] = missing_data
        payload["confidence"] = self._finalize_confidence(
            payload.get("confidence"), len(filtered_refs), len(missing_data)
        )
        return payload

    def _finalize_confidence(
        self,
        confidence_payload: dict[str, Any] | None,
        source_count: int,
        missing_count: int,
    ) -> dict[str, Any]:
        coverage_score = max(0.25, min(0.92, 0.76 + source_count * 0.02 - missing_count * 0.08))
        model_score = 0.65
        model_rationale = "실데이터 sourceRefs 수와 누락 항목 수를 기준으로 보정했습니다."
        if isinstance(confidence_payload, dict):
            model_score = float(confidence_payload.get("score", model_score))
            model_rationale = str(confidence_payload.get("rationale", model_rationale))
        final_score = round(min(model_score, coverage_score), 2)
        if final_score >= 0.75:
            label = "high"
        elif final_score >= 0.55:
            label = "medium"
        else:
            label = "low"
        return {
            "score": final_score,
            "label": label,
            "rationale": model_rationale,
        }
