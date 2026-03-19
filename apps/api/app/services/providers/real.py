from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar

from app.config import Settings
from app.services.clients.alpha_vantage import AlphaVantageClient
from app.services.clients.openai_responses import OpenAIResearchClient
from app.services.errors import ExternalServiceError
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
        self.llm = OpenAIResearchClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
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
        self, *, symbol: str | None, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
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
            raise ExternalServiceError(f"{page_key} 분석에 사용할 실데이터 sourceRefs가 없습니다.")
        return await self.llm.generate_page_response(
            prompt_bundle=prompt_bundle,
            page_key=page_key,
            facts=facts,
            source_refs=dedupe_source_refs(source_refs),
            missing_data=missing_data,
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
