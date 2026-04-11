from __future__ import annotations

from typing import Any


def build_deterministic_page_summary(
    *,
    page_key: str,
    facts: dict[str, Any],
    missing_data: list[dict[str, str]],
    fallback_reason: str,
) -> dict[str, Any]:
    builders = {
        "overview": _build_overview_summary,
        "radar": _build_radar_summary,
        "stocks": _build_stock_summary,
        "history": _build_history_summary,
    }
    builder = builders.get(page_key)
    payload = builder(facts=facts, missing_data=missing_data) if builder else {}
    payload["confidence"] = {
        "score": 0.58,
        "label": "medium",
        "rationale": f"Used deterministic summary fallback because no AI provider was available. {fallback_reason}",
    }
    return payload


def _build_overview_summary(*, facts: dict[str, Any], missing_data: list[dict[str, str]]) -> dict[str, Any]:
    benchmarks = list(facts.get("benchmarks", []))
    sector_proxies = list(facts.get("sectorProxies", []))
    news_items = list(facts.get("notableNews", []))
    treasury = facts.get("treasuryYield10Y", {}) or {}
    top_movers = facts.get("topMovers", {}) or {}

    lead_benchmark = _top_change_item(benchmarks)
    lead_sector = _top_change_item(sector_proxies)
    first_news = news_items[0] if news_items else None
    lead_gainer = (top_movers.get("topGainers") or [{}])[0]

    summary_parts: list[str] = []
    if lead_benchmark:
        summary_parts.append(
            f"{lead_benchmark.get('label', 'Benchmark')} moved {lead_benchmark.get('changePercent', 0):+.2f}%."
        )
    if lead_sector:
        summary_parts.append(
            f"{lead_sector.get('label', 'Lead sector')} is leading the session."
        )
    if treasury:
        summary_parts.append(
            f"US 10Y yield is near {treasury.get('value', 0):.2f}%."
        )
    if first_news:
        summary_parts.append(
            f"Top headline is '{first_news.get('title', '')}'."
        )
    market_summary = _join_sentences(summary_parts) or "Not enough market facts were available to build a deterministic overview summary."

    drivers: list[dict[str, Any]] = []
    if lead_sector:
        drivers.append(
            _sourced_text(
                f"{lead_sector.get('label', 'Lead sector')} should be checked first.",
                lead_sector.get("sourceRefIds", []),
            )
        )
    if first_news:
        drivers.append(
            _sourced_text(
                f"Main news driver: '{first_news.get('title', '')}'.",
                first_news.get("sourceRefIds", []),
            )
        )
    if lead_gainer and lead_gainer.get("symbol"):
        drivers.append(
            _sourced_text(
                f"Top gainer context includes {lead_gainer.get('symbol')}.",
                lead_gainer.get("sourceRefIds", []),
            )
        )

    risks: list[dict[str, Any]] = []
    if treasury:
        change_percent = float(treasury.get("changePercent", 0))
        risk_text = (
            f"US 10Y yield changed {change_percent:+.2f}%p, so rate-sensitive names may stay volatile."
            if change_percent > 0
            else "Rate pressure eased, but concentration risk should still be monitored."
        )
        risks.append(_sourced_text(risk_text, treasury.get("sourceRefIds", [])))
    if missing_data:
        risks.append(
            _sourced_text(
                f"Missing-data count is {len(missing_data)}, so interpretation should stay conservative.",
                [],
            )
        )
    if not risks:
        risks.append(_sourced_text("Watch for sector rotation and concentration risk.", []))

    sector_strength = [
        {
            "sector": proxy.get("label", "Unclassified"),
            "score": round(max(45.0, min(92.0, 60 + float(proxy.get("changePercent", 0)) * 10)), 1),
            "summary": f"Derived from {proxy.get('label', 'this sector')} move and benchmark context.",
            "sourceRefIds": proxy.get("sourceRefIds", []),
        }
        for proxy in sector_proxies[:3]
    ]
    notable_news = [
        {
            "headline": article.get("title", ""),
            "source": article.get("source", "Alpha Vantage"),
            "summary": article.get("summary", ""),
            "impact": _impact_from_sentiment(article.get("sentimentLabel", "")),
            "publishedAt": article.get("publishedAt", ""),
            "url": article.get("url", ""),
            "sourceRefIds": article.get("sourceRefIds", []),
        }
        for article in news_items[:3]
    ]
    return {
        "marketSummary": _sourced_text(market_summary, _merge_ref_ids(lead_benchmark, lead_sector, first_news, treasury)),
        "drivers": drivers[:3] or [_sourced_text("Check the leading sector and top headline first.", [])],
        "risks": risks[:2],
        "sectorStrength": sector_strength,
        "notableNews": notable_news,
    }


def _build_radar_summary(*, facts: dict[str, Any], missing_data: list[dict[str, str]]) -> dict[str, Any]:
    sector_cards = list(facts.get("sectorCards", []))
    top_card = sector_cards[0] if sector_cards else None
    if not top_card:
        text = "Not enough sector data was available to build a radar summary."
        refs: list[str] = []
    else:
        text = (
            f"{top_card.get('sector', 'Lead sector')} is led by {top_card.get('topPick', '')}, "
            f"with {top_card.get('catalyst', 'sector news')} as the main catalyst."
        )
        if missing_data:
            text += " Missing data remains, so event timing should still be checked manually."
        refs = top_card.get("sourceRefIds", [])
    return {"selectedSectorSummary": _sourced_text(text, refs)}


def _build_stock_summary(*, facts: dict[str, Any], missing_data: list[dict[str, str]]) -> dict[str, Any]:
    symbol = facts.get("symbol", "")
    company = facts.get("company", {}) or {}
    issue_cards = list(facts.get("issueCards", []))
    lead_issue = issue_cards[0] if issue_cards else None
    sector = company.get("sector", "") or "related sector"
    if lead_issue:
        text = (
            f"Within {sector}, {symbol} is currently centered on '{lead_issue.get('title', '')}', "
            f"and follow-through should be checked with price and volume together."
        )
        refs = lead_issue.get("sourceRefIds", [])
    else:
        text = f"{symbol} should be evaluated with relative strength and event timing together."
        refs = []
    if missing_data:
        text += " Flow and option data remain unavailable."
    return {"thesis": text, "thesisSourceRefIds": refs}


def _build_history_summary(*, facts: dict[str, Any], missing_data: list[dict[str, str]]) -> dict[str, Any]:
    move_reasons = list(facts.get("moveReasons", []))
    event_timeline = list(facts.get("eventTimeline", []))
    refs = move_reasons[0].get("sourceRefIds", []) if move_reasons else []
    if move_reasons:
        text = " / ".join(reason.get("description", "") for reason in move_reasons[:2])
    elif event_timeline:
        text = " / ".join(event.get("summary", "") for event in event_timeline[:2])
        refs = event_timeline[0].get("sourceRefIds", [])
    else:
        text = "Not enough history facts were available to build a move summary."
    analogs = [
        _sourced_text(
            "Use the overlap between turning points and event timing as the first review pattern.",
            refs,
        )
    ]
    return {
        "moveSummary": _sourced_text(text, refs),
        "analogsOrPatterns": analogs,
    }


def _sourced_text(text: str, source_ref_ids: list[str]) -> dict[str, Any]:
    return {"text": text, "sourceRefIds": list(dict.fromkeys(source_ref_ids))}


def _top_change_item(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    return max(items, key=lambda item: float(item.get("changePercent", 0) or 0))


def _join_sentences(parts: list[str]) -> str:
    return " ".join(part.strip() for part in parts if part).strip()


def _merge_ref_ids(*items: Any) -> list[str]:
    merged: list[str] = []
    for item in items:
        if isinstance(item, dict):
            merged.extend(str(ref_id) for ref_id in item.get("sourceRefIds", []))
    return list(dict.fromkeys(merged))


def _impact_from_sentiment(value: str) -> str:
    normalized = value.lower()
    if "bullish" in normalized or "positive" in normalized:
        return "Positive"
    if "bearish" in normalized or "negative" in normalized:
        return "Negative"
    return "Neutral"
