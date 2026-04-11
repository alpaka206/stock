from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar

from app.config import Settings
from app.services.clients.alpha_vantage import AlphaVantageClient
from app.services.clients.summary_router import ResearchSummaryClient
from app.services.deterministic_summary import build_deterministic_page_summary
from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptBundle
from app.services.providers.base import ResearchProvider
from app.services.research_metrics import (
    compute_stock_score,
    compute_watchlist_score,
    identify_turning_points,
    percent_change,
    simple_return,
    volatility,
    volume_ratio,
)
from app.services.source_refs import (
    build_missing_data,
    build_source_ref,
    collect_source_ref_ids,
    dedupe_source_refs,
)

FetchResultT = TypeVar("FetchResultT")


class RealResearchProvider(ResearchProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.market_data = AlphaVantageClient(
            api_key=settings.alpha_vantage_api_key,
            base_url=settings.alpha_vantage_base_url,
            timeout_seconds=settings.request_timeout_seconds,
            cache_ttl_seconds=settings.provider_cache_ttl_seconds,
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

    async def get_overview(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []

        benchmarks = await self._build_benchmark_cards(source_refs, missing_data)
        sector_proxies = await self._build_sector_proxy_cards(source_refs, missing_data)
        treasury = await self._safe_fetch(
            field="overview.treasuryYield10Y",
            expected_source="Alpha Vantage TREASURY_YIELD",
            missing_data=missing_data,
            fetcher=self.market_data.get_treasury_yield,
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

        top_movers = await self._safe_fetch(
            field="overview.topMovers",
            expected_source="Alpha Vantage TOP_GAINERS_LOSERS",
            missing_data=missing_data,
            fetcher=self.market_data.get_top_movers,
        )
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

        news_items = await self._build_news_items(
            source_refs=source_refs,
            field="overview.news",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
        )

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
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []
        now = datetime.now(timezone.utc)

        sector_map_ref = build_source_ref(
            title="Radar 기본 섹터 매핑",
            kind="internal_config",
            publisher="stock-workspace",
            published_at=now,
            source_key="settings::STOCK_RADAR_SECTORS",
        )
        source_refs.append(sector_map_ref)

        news_items = await self._build_news_items(
            source_refs=source_refs,
            field="radar.news",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=self.settings.radar_symbols,
        )
        news_by_symbol = self._group_news_by_symbol(news_items)

        watchlist_rows: list[dict[str, Any]] = []
        for symbol in self.settings.radar_symbols:
            series = await self._safe_fetch(
                field=f"radar.series.{symbol}",
                expected_source="Alpha Vantage TIME_SERIES_DAILY",
                missing_data=missing_data,
                fetcher=self.market_data.get_daily_series,
                symbol=symbol,
                limit=60,
            )
            if not series or len(series) < 2:
                continue

            series_ref = build_source_ref(
                title=f"{symbol} 일별 시계열",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=series[0]["date"],
                source_key="alpha_vantage::TIME_SERIES_DAILY",
                symbol=symbol,
            )
            source_refs.append(series_ref)
            sentiment_score = self._average_sentiment(news_by_symbol.get(symbol, []))
            score = compute_watchlist_score(series, sentiment_score)
            change_percent = percent_change(series[0]["close"], series[1]["close"])
            watchlist_rows.append(
                {
                    "symbol": symbol,
                    "sector": self.settings.radar_sector_map.get(symbol, "미분류"),
                    "price": round(series[0]["close"], 2),
                    "changePercent": change_percent,
                    "return5d": simple_return(series, 5),
                    "return20d": simple_return(series, 20),
                    "volumeRatio": volume_ratio(series),
                    "volatility20d": volatility(series),
                    "sentimentScore": round(sentiment_score, 2),
                    "score": score,
                    "condition": self._watchlist_condition(score),
                    "sourceRefIds": [series_ref["id"], sector_map_ref["id"]],
                }
            )

        if not watchlist_rows:
            raise ExternalServiceError("radar 화면에 사용할 실데이터 watchlist를 만들지 못했습니다.")

        facts = {
            "watchlistRows": sorted(watchlist_rows, key=lambda item: item["score"], reverse=True),
            "newsItems": news_items,
            "sectorMap": self.settings.radar_sector_map,
        }
        payload = await self._summarize(
            page_key="radar",
            prompt_bundle=prompt_bundle,
            facts=facts,
            source_refs=source_refs,
            missing_data=missing_data,
        )
        return self._finalize_payload(payload, source_refs, missing_data)

    async def get_stock_detail(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        return await self._get_stock_detail_v2(symbol=symbol, prompt_bundle=prompt_bundle)
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = [
            build_missing_data(
                "flowSummary",
                "기관·외국인 수급 전용 데이터 소스가 아직 연결되지 않았습니다.",
                "전용 수급 provider",
            ),
            build_missing_data(
                "optionsShortSummary",
                "옵션·공매도 전용 데이터 소스가 아직 연결되지 않았습니다.",
                "옵션/공매도 provider",
            ),
        ]

        series = await self._safe_fetch(
            field=f"stocks.series.{symbol}",
            expected_source="Alpha Vantage TIME_SERIES_DAILY",
            missing_data=missing_data,
            fetcher=self.market_data.get_daily_series,
            symbol=symbol,
            limit=90,
        )
        overview = await self._safe_fetch(
            field=f"stocks.overview.{symbol}",
            expected_source="Alpha Vantage OVERVIEW",
            missing_data=missing_data,
            fetcher=self.market_data.get_company_overview,
            symbol=symbol,
        )
        news_items = await self._build_news_items(
            source_refs=source_refs,
            field=f"stocks.news.{symbol}",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=[symbol],
        )
        if not series or len(series) < 2 or not overview:
            raise ExternalServiceError(f"{symbol} 상세 분석에 필요한 실데이터를 충분히 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{symbol} 일별 시계열",
            kind="market_data",
            publisher="Alpha Vantage",
            published_at=series[0]["date"],
            source_key="alpha_vantage::TIME_SERIES_DAILY",
            symbol=symbol,
        )
        overview_ref = build_source_ref(
            title=f"{symbol} 기업 개요",
            kind="fundamentals",
            publisher="Alpha Vantage",
            published_at=datetime.now(timezone.utc),
            source_key="alpha_vantage::OVERVIEW",
            symbol=symbol,
        )
        source_refs.extend([series_ref, overview_ref])

        sentiment_score = self._average_sentiment(news_items)
        score = compute_stock_score(series, sentiment_score)
        facts = {
            "symbol": symbol,
            "company": overview,
            "latestPrice": round(series[0]["close"], 2),
            "changePercent": percent_change(series[0]["close"], series[1]["close"]),
            "return5d": simple_return(series, 5),
            "return20d": simple_return(series, 20),
            "volumeRatio": volume_ratio(series),
            "volatility20d": volatility(series),
            "scoreModel": {**score, "sourceRefIds": [series_ref["id"], overview_ref["id"]]},
            "newsItems": news_items,
            "missingDataHints": missing_data,
        }
        payload = await self._summarize(
            page_key="stocks",
            prompt_bundle=prompt_bundle,
            facts=facts,
            source_refs=source_refs,
            missing_data=missing_data,
        )
        return self._finalize_payload(payload, source_refs, missing_data)

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
        target_symbol = symbol or self.settings.radar_symbols[0]
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = [
            build_missing_data(
                "history.lookback",
                "무료 Alpha Vantage 일별 시계열은 compact 범위 중심으로 사용합니다.",
                "Alpha Vantage premium 또는 별도 히스토리 provider",
            )
        ]

        series = await self._safe_fetch(
            field=f"history.series.{target_symbol}",
            expected_source="Alpha Vantage TIME_SERIES_DAILY",
            missing_data=missing_data,
            fetcher=self.market_data.get_daily_series,
            symbol=target_symbol,
            limit=100,
        )
        news_items = await self._build_news_items(
            source_refs=source_refs,
            field=f"history.news.{target_symbol}",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=[target_symbol],
        )
        if not series or len(series) < 2:
            raise ExternalServiceError(f"{target_symbol} 히스토리 리플레이용 시계열을 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{target_symbol} 히스토리 일별 시계열",
            kind="market_data",
            publisher="Alpha Vantage",
            published_at=series[0]["date"],
            source_key="alpha_vantage::TIME_SERIES_DAILY",
            symbol=target_symbol,
        )
        source_refs.append(series_ref)
        turning_points = identify_turning_points(series)
        facts = {
            "symbol": target_symbol,
            "latestPrice": round(series[0]["close"], 2),
            "return5d": simple_return(series, 5),
            "return20d": simple_return(series, 20),
            "turningPoints": [
                {**item, "sourceRefIds": [series_ref["id"]]} for item in turning_points
            ],
            "newsItems": news_items,
        }
        payload = await self._summarize(
            page_key="history",
            prompt_bundle=prompt_bundle,
            facts=facts,
            source_refs=source_refs,
            missing_data=missing_data,
        )
        return self._finalize_payload(payload, source_refs, missing_data)

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

        news_items = await self._build_news_items(
            source_refs=source_refs,
            field="radar.news",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=self.settings.radar_symbols,
        )
        news_by_symbol = self._group_news_by_symbol(news_items)

        raw_rows: list[dict[str, Any]] = []
        for symbol in self.settings.radar_symbols:
            series = await self._safe_fetch(
                field=f"radar.series.{symbol}",
                expected_source="Alpha Vantage TIME_SERIES_DAILY",
                missing_data=missing_data,
                fetcher=self.market_data.get_daily_series,
                symbol=symbol,
                limit=60,
            )
            if not series or len(series) < 2:
                continue

            series_ref = build_source_ref(
                title=f"{symbol} 일별 시계열",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=series[0]["date"],
                source_key="alpha_vantage::TIME_SERIES_DAILY",
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

        watchlist_rows = self._build_radar_watchlist_rows(raw_rows, news_by_symbol)
        sector_cards = self._build_radar_sector_cards(watchlist_rows)
        broker_reports = self._build_radar_broker_reports(sector_cards)
        key_schedule = self._build_radar_schedule(sector_cards)
        key_issues = self._build_radar_key_issues(news_items)
        top_picks = self._build_radar_top_picks(sector_cards)
        folder_tree = self._build_radar_folder_tree(watchlist_rows)

        payload = await self._summarize(
            page_key="radar",
            prompt_bundle=prompt_bundle,
            facts={
                "selectedSector": sector_cards[0]["sector"] if sector_cards else "",
                "watchlistRows": watchlist_rows,
                "sectorCards": sector_cards,
                "keyIssues": key_issues,
                "topPicks": top_picks,
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
        return self._finalize_payload(payload, source_refs, missing_data)

    async def _get_stock_detail_v2(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] = []
        missing_data: list[dict[str, str]] = []

        series = await self._safe_fetch(
            field=f"stocks.series.{symbol}",
            expected_source="Alpha Vantage TIME_SERIES_DAILY",
            missing_data=missing_data,
            fetcher=self.market_data.get_daily_series,
            symbol=symbol,
            limit=90,
        )
        overview = await self._safe_fetch(
            field=f"stocks.overview.{symbol}",
            expected_source="Alpha Vantage OVERVIEW",
            missing_data=missing_data,
            fetcher=self.market_data.get_company_overview,
            symbol=symbol,
        )
        news_items = await self._build_news_items(
            source_refs=source_refs,
            field=f"stocks.news.{symbol}",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=[symbol],
        )
        if not series or len(series) < 2 or not overview:
            raise ExternalServiceError(f"{symbol} 상세 분석에 필요한 데이터를 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{symbol} 일별 시계열",
            kind="market_data",
            publisher="Alpha Vantage",
            published_at=series[0]["date"],
            source_key="alpha_vantage::TIME_SERIES_DAILY",
            symbol=symbol,
        )
        overview_ref = build_source_ref(
            title=f"{symbol} 기업 개요",
            kind="fundamentals",
            publisher="Alpha Vantage",
            published_at=datetime.now(timezone.utc),
            source_key="alpha_vantage::OVERVIEW",
            symbol=symbol,
        )
        source_refs.extend([series_ref, overview_ref])

        score_model = compute_stock_score(series, self._average_sentiment(news_items))
        price_series = self._build_price_series(series, limit=60)
        event_markers = self._build_stock_event_markers(symbol, news_items)
        indicator_guides = self._build_stock_indicator_guides(series)
        rule_preset_definitions = self._build_stock_rule_preset_definitions()
        score_summary = self._build_stock_score_summary(score_model)
        issue_cards = self._build_stock_issue_cards(symbol, overview, news_items)
        related_symbols = self._build_related_symbols(symbol, overview.get("sector", ""))

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
                "relatedSymbols": related_symbols,
            },
            source_refs=source_refs,
            missing_data=missing_data,
        )
        payload["instrument"] = self._build_stock_instrument(symbol, overview)
        payload["latestPrice"] = round(series[0]["close"], 2)
        payload["changePercent"] = percent_change(series[0]["close"], series[1]["close"])
        payload["thesis"] = payload.get("thesis") or self._fallback_stock_thesis(
            symbol=symbol,
            overview=overview,
            news_items=news_items,
        )
        payload["priceSeries"] = price_series
        payload["eventMarkers"] = event_markers
        payload["indicatorGuides"] = indicator_guides
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

        series = await self._safe_fetch(
            field=f"history.series.{target_symbol}",
            expected_source="Alpha Vantage TIME_SERIES_DAILY",
            missing_data=missing_data,
            fetcher=self.market_data.get_daily_series,
            symbol=target_symbol,
            limit=100,
        )
        news_items = await self._build_news_items(
            source_refs=source_refs,
            field=f"history.news.{target_symbol}",
            expected_source="Alpha Vantage NEWS_SENTIMENT",
            missing_data=missing_data,
            tickers=[target_symbol],
        )
        if not series or len(series) < 2:
            raise ExternalServiceError(f"{target_symbol} 히스토리 시계열을 가져오지 못했습니다.")

        series_ref = build_source_ref(
            title=f"{target_symbol} 히스토리 일별 시계열",
            kind="market_data",
            publisher="Alpha Vantage",
            published_at=series[0]["date"],
            source_key="alpha_vantage::TIME_SERIES_DAILY",
            symbol=target_symbol,
        )
        source_refs.append(series_ref)

        filtered_series = self._slice_history_series(
            series=series,
            range_value=range,
            from_date=from_date,
            to_date=to_date,
        )
        price_series = self._build_price_series(filtered_series, limit=len(filtered_series))
        turning_points = identify_turning_points(filtered_series, limit=4)
        event_timeline = self._build_history_event_timeline(
            symbol=target_symbol,
            news_items=news_items,
            turning_points=turning_points,
            filtered_series=filtered_series,
        )
        move_reasons = self._build_history_move_reasons(turning_points, series_ref["id"])
        overlapping_indicators = self._build_history_overlaps(
            filtered_series, turning_points, series_ref["id"]
        )
        event_markers = self._build_history_event_markers(event_timeline)

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
        payload["rangeLabel"] = self._history_range_label(
            price_series=price_series,
            from_date=from_date,
            to_date=to_date,
        )
        payload["availableRanges"] = self._history_available_ranges()
        payload["priceSeries"] = price_series
        payload["eventMarkers"] = event_markers
        payload["eventTimeline"] = event_timeline
        payload["moveSummary"] = payload.get("moveSummary") or {
            "text": self._fallback_history_summary(move_reasons),
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

    def _build_radar_watchlist_rows(
        self,
        rows: list[dict[str, Any]],
        news_by_symbol: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        ordered = sorted(rows, key=lambda item: item["score"], reverse=True)
        hydrated: list[dict[str, Any]] = []
        for row in ordered:
            symbol = row["symbol"]
            sector = row["sector"]
            top_news = news_by_symbol.get(symbol, [])
            thesis = top_news[0]["summary"] if top_news else f"{sector} 내 상대 강도 상위 종목입니다."
            hydrated.append(
                {
                    "symbol": symbol,
                    "name": self._instrument_name(symbol),
                    "securityCode": self._security_code(symbol),
                    "sector": sector,
                    "folderId": self._radar_folder_id(sector, row["score"]),
                    "tags": self._radar_tags(sector, row["score"]),
                    "price": row["price"],
                    "changePercent": row["changePercent"],
                    "volumeRatio": row["volumeRatio"],
                    "relativeStrength": self._relative_strength_score(row),
                    "score": row["score"],
                    "nextEvent": self._radar_next_event(sector),
                    "thesis": thesis,
                    "condition": row["condition"],
                    "sourceRefIds": row["sourceRefIds"],
                }
            )
        return hydrated

    def _build_radar_sector_cards(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row["sector"], []).append(row)

        cards: list[dict[str, Any]] = []
        for sector, sector_rows in grouped.items():
            ordered = sorted(sector_rows, key=lambda item: item["score"], reverse=True)
            avg_score = round(
                sum(float(item["score"]) for item in sector_rows) / len(sector_rows), 1
            )
            top_row = ordered[0]
            cards.append(
                {
                    "sector": sector,
                    "score": avg_score,
                    "thesis": f"{sector}에서 {top_row['symbol']}가 상대 강도와 점수 기준으로 가장 앞섭니다.",
                    "catalyst": self._radar_sector_catalyst(sector),
                    "topPick": top_row["symbol"],
                    "sourceRefIds": top_row["sourceRefIds"],
                }
            )

        cards.sort(key=lambda item: item["score"], reverse=True)
        return cards

    def _build_radar_broker_reports(self, sector_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        reports: list[dict[str, Any]] = []
        for index, card in enumerate(sector_cards[:3]):
            reports.append(
                {
                    "sector": card["sector"],
                    "house": f"Broker {chr(65 + index)}",
                    "symbol": card["topPick"],
                    "stance": "우선 검토 유지",
                    "summary": f"{card['sector']}에서 {card['topPick']}가 점수와 촉매 기준으로 가장 앞섭니다.",
                    "sourceRefIds": card["sourceRefIds"],
                }
            )
        return reports

    def _build_radar_schedule(self, sector_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        schedule_times = ["09:10", "11:20", "14:00"]
        items: list[dict[str, Any]] = []
        for index, card in enumerate(sector_cards[:3]):
            items.append(
                {
                    "sector": card["sector"],
                    "time": schedule_times[index],
                    "title": f"{card['sector']} 체크",
                    "note": f"{card['topPick']} 거래량과 이벤트 일정을 확인합니다.",
                    "sourceRefIds": card["sourceRefIds"],
                }
            )
        return items

    def _build_radar_key_issues(self, news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        for article in news_items[:3]:
            primary_symbol = article.get("tickers", [""])[0] if article.get("tickers") else ""
            issues.append(
                {
                    "headline": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "impact": self._impact_from_sentiment(article.get("sentimentLabel", "")),
                    "sector": self.settings.radar_sector_map.get(primary_symbol, ""),
                    "sourceRefIds": article.get("sourceRefIds", []),
                }
            )
        return issues

    def _build_radar_top_picks(self, sector_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "sector": card["sector"],
                "symbol": card["topPick"],
                "reason": f"{card['sector']}에서 점수와 촉매가 가장 좋습니다.",
                "score": card["score"],
                "sourceRefIds": card["sourceRefIds"],
            }
            for card in sector_cards[:3]
        ]

    def _build_radar_folder_tree(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row["sector"], []).append(row)

        children = [
            {
                "id": self._slugify(sector),
                "label": sector,
                "count": len(sector_rows),
                "description": f"{sector} 관련 우선 검토 종목",
                "tags": [sector],
                "children": [],
            }
            for sector, sector_rows in grouped.items()
        ]
        return [
            {
                "id": "all",
                "label": "전체 워치리스트",
                "count": len(rows),
                "description": "현재 radar에서 보는 전체 종목",
                "tags": ["전체"],
                "children": children,
            }
        ]

    def _build_stock_instrument(self, symbol: str, overview: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "name": overview.get("name", symbol),
            "exchange": "NASDAQ",
            "securityCode": self._security_code(symbol),
            "sector": overview.get("sector", "") or "미분류",
            "marketCap": self._format_market_cap(overview.get("marketCapitalization", 0.0)),
        }

    def _build_price_series(self, series: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        selected = list(reversed(series[:limit]))
        return [
            {
                "date": row["date"],
                "label": row["date"][5:].replace("-", "/"),
                "close": round(float(row["close"]), 2),
                "volume": round(float(row["volume"]) / 1_000_000, 2),
            }
            for row in selected
        ]

    def _build_stock_event_markers(
        self, symbol: str, news_items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        markers: list[dict[str, Any]] = []
        for index, article in enumerate(news_items[:3]):
            markers.append(
                {
                    "id": f"{symbol.lower()}-event-{index + 1}",
                    "label": "뉴스",
                    "tone": self._tone_from_sentiment_label(article.get("sentimentLabel", "")),
                    "date": article.get("publishedAt", "")[:10],
                    "pointLabel": "",
                    "title": article.get("title", ""),
                    "detail": article.get("summary", ""),
                    "href": "",
                }
            )
        return markers

    def _build_stock_indicator_guides(self, series: list[dict[str, Any]]) -> list[dict[str, Any]]:
        recent = series[:20]
        support = round(min(row["low"] for row in recent), 2)
        resistance = round(max(row["high"] for row in recent), 2)
        trend_base = round(sum(row["close"] for row in recent) / len(recent), 2)
        return [
            {
                "id": "support",
                "label": "지지 구간",
                "value": support,
                "tone": "positive",
                "description": "최근 눌림 구간 방어선입니다.",
                "enabled": True,
            },
            {
                "id": "trend-base",
                "label": "추세 기준선",
                "value": trend_base,
                "tone": "neutral",
                "description": "중기 추세 유지 판단선입니다.",
                "enabled": True,
            },
            {
                "id": "resistance",
                "label": "저항 구간",
                "value": resistance,
                "tone": "negative",
                "description": "단기 과열 경계 구간입니다.",
                "enabled": True,
            },
            {
                "id": "volume-spike",
                "label": "거래량 배수",
                "value": volume_ratio(series),
                "tone": "positive",
                "description": "추세 신뢰도를 보는 거래량 기준입니다.",
                "enabled": True,
            },
            {
                "id": "relative-strength",
                "label": "상대강도",
                "value": round(50 + max(simple_return(series, 20), -10) * 2, 2),
                "tone": "positive",
                "description": "리더십 유지 여부를 확인하는 값입니다.",
                "enabled": True,
            },
            {
                "id": "volatility-guard",
                "label": "변동성 경계",
                "value": volatility(series),
                "tone": "negative",
                "description": "이벤트 직후 흔들림 확대 가능성을 봅니다.",
                "enabled": False,
            },
        ]

    def _build_stock_rule_preset_definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "support-hold",
                "label": "지지선 유지",
                "description": "지지 구간 위에서 종가가 유지되는지 확인합니다.",
                "enabledByDefault": True,
                "tone": "positive",
                "guideIds": ["support"],
                "controlsEventMarkers": False,
            },
            {
                "id": "trend-base",
                "label": "추세 기준선",
                "description": "중기 추세 기준선 위에서 종가가 유지되는지 확인합니다.",
                "enabledByDefault": True,
                "tone": "neutral",
                "guideIds": ["trend-base"],
                "controlsEventMarkers": False,
            },
            {
                "id": "volume-spike",
                "label": "거래량 배수",
                "description": "거래량이 추세를 지지하는지 확인합니다.",
                "enabledByDefault": True,
                "tone": "positive",
                "guideIds": ["volume-spike", "volume"],
                "controlsEventMarkers": False,
            },
            {
                "id": "relative-strength",
                "label": "상대강도",
                "description": "같은 섹터 내 리더 여부를 확인합니다.",
                "enabledByDefault": True,
                "tone": "positive",
                "guideIds": ["relative-strength"],
                "controlsEventMarkers": False,
            },
            {
                "id": "volatility-guard",
                "label": "변동성 경계",
                "description": "과열 뒤 흔들림 확대 여부를 경고합니다.",
                "enabledByDefault": False,
                "tone": "negative",
                "guideIds": ["volatility-guard", "volatility"],
                "controlsEventMarkers": False,
            },
            {
                "id": "event-window",
                "label": "이벤트 창 관리",
                "description": "실적과 행사 직전후 이벤트 마커를 확인합니다.",
                "enabledByDefault": True,
                "tone": "neutral",
                "guideIds": [],
                "controlsEventMarkers": True,
            },
        ]
        return [
            {"id": "support-hold", "label": "지지선 유지", "description": "지지 구간 위 종가 유지 여부를 봅니다.", "enabledByDefault": True, "tone": "positive"},
            {"id": "trend-base", "label": "추세선 회복", "description": "중기 추세 기준선 위 유지 여부를 확인합니다.", "enabledByDefault": True, "tone": "neutral"},
            {"id": "volume-spike", "label": "거래량 배수", "description": "거래량이 추세를 지지하는지 확인합니다.", "enabledByDefault": True, "tone": "positive"},
            {"id": "relative-strength", "label": "상대강도", "description": "같은 섹터 내 리더십 유지 여부를 봅니다.", "enabledByDefault": True, "tone": "positive"},
            {"id": "volatility-guard", "label": "변동성 경계", "description": "과열 뒤 흔들림 확대를 경고합니다.", "enabledByDefault": False, "tone": "negative"},
            {"id": "event-window", "label": "이벤트 창 관리", "description": "실적과 행사 직전후 과열 여부를 체크합니다.", "enabledByDefault": True, "tone": "neutral"},
        ]

    def _build_stock_score_summary(self, score_model: dict[str, Any]) -> dict[str, Any]:
        breakdown = score_model["breakdown"]
        return {
            "total": score_model["total"],
            "confidence": {
                "score": 0.78,
                "label": "medium",
                "rationale": "가격, 거래량, 뉴스가 함께 있는 구간이지만 수급/옵션 데이터는 빠져 있습니다.",
            },
            "breakdown": [
                {"label": "기술 추세", "score": breakdown["technical"], "summary": "가격과 거래량 기준 기술 추세 점수입니다."},
                {"label": "수급/유동성", "score": breakdown["flow"], "summary": "뉴스 감성과 거래량을 반영한 유동성 점수입니다."},
                {"label": "촉매/이슈", "score": breakdown["catalyst"], "summary": "최근 뉴스와 모멘텀을 반영한 촉매 점수입니다."},
                {"label": "리스크 관리", "score": breakdown["risk"], "summary": "변동성과 하락 구간 민감도를 반영한 리스크 점수입니다."},
            ],
        }

    def _build_stock_issue_cards(
        self, symbol: str, overview: dict[str, Any], news_items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        sector = overview.get("sector", "") or self.settings.radar_sector_map.get(symbol, "")
        issues: list[dict[str, Any]] = []
        for article in news_items[:3]:
            issues.append(
                {
                    "title": article.get("title", ""),
                    "source": article.get("source", "Alpha Vantage"),
                    "summary": article.get("summary", ""),
                    "tone": self._tone_from_sentiment_label(article.get("sentimentLabel", "")),
                    "category": "종목" if symbol in article.get("tickers", []) else "시황",
                    "href": f"/history?symbol={symbol}",
                    "sourceRefIds": article.get("sourceRefIds", []),
                }
            )
        if not issues:
            issues.append(
                {
                    "title": f"{sector or '섹터'} 컨텍스트",
                    "source": "derived",
                    "summary": f"{sector or '관련 섹터'} 흐름을 함께 체크해야 합니다.",
                    "tone": "neutral",
                    "category": "섹터",
                    "href": f"/radar?sector={sector}" if sector else "/radar",
                    "sourceRefIds": [],
                }
            )
        return issues

    def _build_related_symbols(self, symbol: str, sector: str) -> list[str]:
        same_sector = [
            item
            for item in self.settings.radar_symbols
            if item != symbol and self.settings.radar_sector_map.get(item, "") == sector
        ]
        fallback = [item for item in self.settings.radar_symbols if item != symbol]
        return (same_sector or fallback)[:3]

    def _slice_history_series(
        self,
        *,
        series: list[dict[str, Any]],
        range_value: str | None,
        from_date: str | None,
        to_date: str | None,
    ) -> list[dict[str, Any]]:
        filtered = series
        if from_date or to_date:
            filtered = [
                row
                for row in series
                if (not from_date or row["date"] >= from_date)
                and (not to_date or row["date"] <= to_date)
            ]
        elif range_value == "1m":
            filtered = series[:22]
        elif range_value == "3m":
            filtered = series[:66]
        elif range_value == "6m":
            filtered = series[:100]
        elif range_value == "event":
            filtered = series[:30]

        return filtered if len(filtered) >= 2 else series[:30]

    def _build_history_event_timeline(
        self,
        *,
        symbol: str,
        news_items: list[dict[str, Any]],
        turning_points: list[dict[str, Any]],
        filtered_series: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        series_dates = sorted({str(row["date"]) for row in filtered_series if row.get("date")})
        events: list[dict[str, Any]] = []
        for index, turning_point in enumerate(turning_points[:3]):
            tone = "positive" if turning_point["move"] > 0 else "negative"
            events.append(
                {
                    "id": f"{symbol.lower()}-turning-{index + 1}",
                    "date": turning_point["date"],
                    "title": "가격 변곡점",
                    "category": "차트",
                    "summary": f"하루 변동폭 {turning_point['move']:.2f}% 구간입니다.",
                    "reaction": f"{turning_point['move']:+.2f}%",
                    "tone": tone,
                    "source": "price-series",
                    "url": "",
                    "sourceRefIds": turning_point.get("sourceRefIds", []),
                }
            )

        filtered_news: list[tuple[dict[str, Any], str]] = []
        for article in news_items:
            aligned_date = self._align_history_event_date(
                str(article.get("publishedAt", ""))[:10],
                series_dates,
            )
            if not aligned_date:
                continue
            filtered_news.append((article, aligned_date))
            if len(filtered_news) >= 2:
                break

        for index, (article, aligned_date) in enumerate(filtered_news):
            events.append(
                {
                    "id": f"{symbol.lower()}-news-{index + 1}",
                    "date": aligned_date,
                    "title": article.get("title", ""),
                    "category": "뉴스",
                    "summary": article.get("summary", ""),
                    "reaction": article.get("sentimentLabel", ""),
                    "tone": self._tone_from_sentiment_label(article.get("sentimentLabel", "")),
                    "source": article.get("source", "Alpha Vantage"),
                    "url": article.get("url", ""),
                    "sourceRefIds": article.get("sourceRefIds", []),
                }
            )

        events.sort(key=lambda item: item["date"])
        return events

    def _align_history_event_date(
        self, event_date: str, series_dates: list[str]
    ) -> str | None:
        if not event_date or not series_dates:
            return None

        earliest = series_dates[0]
        latest = series_dates[-1]
        if event_date < earliest or event_date > latest:
            return None

        aligned_date: str | None = None
        for candidate in series_dates:
            if candidate <= event_date:
                aligned_date = candidate
                continue
            break

        return aligned_date or earliest

    def _build_history_move_reasons(
        self, turning_points: list[dict[str, Any]], source_ref_id: str
    ) -> list[dict[str, Any]]:
        reasons: list[dict[str, Any]] = []
        for turning_point in turning_points[:3]:
            tone = "positive" if turning_point["move"] > 0 else "negative"
            reasons.append(
                {
                    "label": "급등 구간 핵심 이유" if tone == "positive" else "조정 구간 핵심 이유",
                    "description": f"{turning_point['date']} 전후 가격 변동이 {turning_point['move']:+.2f}%로 커졌습니다.",
                    "tone": tone,
                    "relatedDate": turning_point["date"],
                    "sourceRefIds": [source_ref_id],
                }
            )

        if not reasons:
            reasons.append(
                {
                    "label": "데이터 부족",
                    "description": "유효한 변곡점을 찾지 못했습니다.",
                    "tone": "neutral",
                    "relatedDate": "",
                    "sourceRefIds": [source_ref_id],
                }
            )
        return reasons

    def _build_history_overlaps(
        self,
        series: list[dict[str, Any]],
        turning_points: list[dict[str, Any]],
        source_ref_id: str,
    ) -> list[dict[str, Any]]:
        overlap_items: list[dict[str, Any]] = []
        if turning_points:
            overlap_items.append(
                {
                    "label": "거래량 + 변동성 중첩",
                    "detail": f"최근 변곡점 구간의 변동성은 {volatility(series):.2f} 수준입니다.",
                    "tone": "positive" if turning_points[0]["move"] > 0 else "negative",
                    "relatedDate": turning_points[0]["date"],
                    "sourceRefIds": [source_ref_id],
                }
            )
        overlap_items.append(
            {
                "label": "거래량 배수 체크",
                "detail": f"최근 거래량 배수는 {volume_ratio(series):.2f}배입니다.",
                "tone": "neutral",
                "relatedDate": series[0]["date"],
                "sourceRefIds": [source_ref_id],
            }
        )
        return overlap_items

    def _build_history_event_markers(self, event_timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "id": event["id"],
                "label": event["category"],
                "tone": event["tone"],
                "date": event["date"],
                "pointLabel": "",
                "title": event["title"],
                "detail": event["summary"],
                "href": event.get("url", ""),
            }
            for event in event_timeline
        ]

    def _history_available_ranges(self) -> list[dict[str, str]]:
        return [
            {"value": "1m", "label": "1개월"},
            {"value": "3m", "label": "3개월"},
            {"value": "6m", "label": "6개월"},
            {"value": "event", "label": "이벤트 구간"},
        ]

    def _history_range_label(
        self,
        *,
        price_series: list[dict[str, Any]],
        from_date: str | None,
        to_date: str | None,
    ) -> str:
        if from_date or to_date:
            return f"{from_date or price_series[0]['date']} ~ {to_date or price_series[-1]['date']}"
        return f"{price_series[0]['date']} ~ {price_series[-1]['date']}"

    def _fallback_radar_sector_summary(self, sector_card: dict[str, Any] | None) -> str:
        if not sector_card:
            return "선택 섹터 요약을 만들기 위한 데이터가 아직 충분하지 않습니다."
        return (
            f"{sector_card['sector']} 섹터에서 {sector_card['topPick']}가 가장 앞서며, "
            f"{sector_card['catalyst']}를 핵심 촉매로 봅니다."
        )

    def _fallback_stock_thesis(
        self,
        *,
        symbol: str,
        overview: dict[str, Any],
        news_items: list[dict[str, Any]],
    ) -> str:
        sector = overview.get("sector", "") or self.settings.radar_sector_map.get(symbol, "")
        if news_items:
            return f"{sector} 흐름 안에서 최근 뉴스가 {symbol}의 모멘텀을 지지하지만, 과열 구간 여부는 가격 레벨과 거래량으로 다시 확인해야 합니다."
        return f"{sector} 내 핵심 종목이지만, 추가 추세 확인 전에는 이벤트와 거래량을 같이 점검해야 합니다."

    def _fallback_history_summary(self, move_reasons: list[dict[str, Any]]) -> str:
        if not move_reasons:
            return "과거 움직임 요약을 만들 데이터가 아직 충분하지 않습니다."
        return " / ".join(reason["description"] for reason in move_reasons[:2])

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
            raise ExternalServiceError(f"{page_key} ??? ??? ???? sourceRefs? ????.")
        deduped_source_refs = dedupe_source_refs(source_refs)
        try:
            return await self.llm.generate_page_response(
                prompt_bundle=prompt_bundle,
                page_key=page_key,
                facts=facts,
                source_refs=deduped_source_refs,
                missing_data=missing_data,
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
        for symbol, label in self.settings.overview_benchmarks.items():
            series = await self._safe_fetch(
                field=f"overview.benchmark.{symbol}",
                expected_source="Alpha Vantage TIME_SERIES_DAILY",
                missing_data=missing_data,
                fetcher=self.market_data.get_daily_series,
                symbol=symbol,
                limit=30,
            )
            if not series or len(series) < 2:
                continue
            ref = build_source_ref(
                title=f"{label} 일별 시계열",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=series[0]["date"],
                source_key="alpha_vantage::TIME_SERIES_DAILY",
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
        for symbol, label in self.settings.sector_proxies.items():
            series = await self._safe_fetch(
                field=f"overview.sectorProxy.{symbol}",
                expected_source="Alpha Vantage TIME_SERIES_DAILY",
                missing_data=missing_data,
                fetcher=self.market_data.get_daily_series,
                symbol=symbol,
                limit=30,
            )
            if not series or len(series) < 2:
                continue
            ref = build_source_ref(
                title=f"{label} ETF 일별 시계열",
                kind="market_data",
                publisher="Alpha Vantage",
                published_at=series[0]["date"],
                source_key="alpha_vantage::TIME_SERIES_DAILY",
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
    ) -> list[dict[str, Any]]:
        articles = await self._safe_fetch(
            field=field,
            expected_source=expected_source,
            missing_data=missing_data,
            fetcher=self.market_data.get_news_sentiment,
            tickers=tickers,
            limit=8,
        )
        if not articles:
            return []

        hydrated: list[dict[str, Any]] = []
        for article in articles:
            ref = build_source_ref(
                title=article["title"],
                kind="news",
                publisher=article["source"] or "Alpha Vantage",
                published_at=article["publishedAt"],
                source_key="alpha_vantage::NEWS_SENTIMENT",
                url=article["url"],
                symbol=",".join(article["tickers"]),
            )
            source_refs.append(ref)
            hydrated.append({**article, "sourceRefIds": [ref["id"]]})
        return hydrated

    async def _safe_fetch(
        self,
        *,
        field: str,
        expected_source: str,
        missing_data: list[dict[str, str]],
        fetcher: Callable[..., Awaitable[FetchResultT]],
        **kwargs: Any,
    ) -> FetchResultT | None:
        try:
            return await fetcher(**kwargs)
        except ExternalServiceError as exc:
            missing_data.append(build_missing_data(field, str(exc), expected_source))
            return None

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
