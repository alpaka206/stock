from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.providers.history_builders import (  # noqa: E402
    build_history_event_markers,
    build_history_event_timeline,
    build_history_move_reasons,
    build_history_overlaps,
    history_available_ranges,
    history_range_label,
    slice_history_series,
)
from app.services.providers.stock_builders import (  # noqa: E402
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


def build_series(days: int = 140) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for index in range(days):
        close = 120 + (days - index) * 0.9
        rows.append(
            {
                "date": f"2026-03-{(days - index - 1) % 28 + 1:02d}",
                "open": close - 0.4,
                "high": close + 1.2,
                "low": close - 1.4,
                "close": close,
                "volume": 1_000_000 + (days - index) * 20_000,
            }
        )
    return rows


def main() -> int:
    series = build_series()
    news_items = [
        {
            "title": "NVDA demand rises",
            "source": "Alpha Vantage",
            "summary": "가속기 수요가 강합니다.",
            "sentimentLabel": "Bullish",
            "tickers": ["NVDA"],
            "publishedAt": series[4]["date"],
            "url": "https://example.com/news",
            "sourceRefIds": ["news-ref"],
        }
    ]
    overview = {
        "name": "NVIDIA",
        "exchange": "NASDAQ",
        "sector": "반도체",
        "marketCapitalization": 2_500_000_000_000,
    }
    tone = lambda value: "positive" if value.lower().startswith("bull") else "neutral"

    instrument = build_stock_instrument(
        "NVDA",
        overview,
        security_code=lambda symbol: f"{symbol}-US",
        format_market_cap=lambda value: f"{value / 1_000_000_000_000:.2f}T",
    )
    price_series = build_price_series(series, limit=60)
    markers = build_stock_event_markers("NVDA", news_items, tone_from_sentiment_label=tone)
    guides = build_stock_indicator_guides(series)
    overlays = build_stock_chart_overlays(series, limit=60)
    metrics = build_stock_technical_metrics(series, "series-ref")
    patterns = build_stock_pattern_cards(series, "series-ref")
    presets = build_stock_rule_preset_definitions()
    score_summary = build_stock_score_summary(
        {"total": 82, "breakdown": {"technical": 80, "flow": 78, "catalyst": 84, "risk": 76}}
    )
    issues = build_stock_issue_cards(
        "NVDA",
        overview,
        news_items,
        sector_by_symbol={"NVDA": "반도체", "AMD": "반도체"},
        tone_from_sentiment_label=tone,
    )
    related = build_related_symbols(
        "NVDA",
        "반도체",
        radar_symbols=["NVDA", "AMD", "MSFT"],
        sector_by_symbol={"NVDA": "반도체", "AMD": "반도체", "MSFT": "소프트웨어"},
    )

    if instrument["securityCode"] != "NVDA-US":
        raise AssertionError("stock instrument should use injected security code")
    if len(price_series) != 60 or not markers or not guides:
        raise AssertionError("stock builders should produce chart primitives")
    if not overlays or not metrics or not patterns or len(presets) < 6:
        raise AssertionError("stock technical builders should produce analysis data")
    if score_summary["total"] != 82 or issues[0]["category"] != "종목":
        raise AssertionError("stock score/issues should preserve expected fields")
    if related != ["AMD"]:
        raise AssertionError("related symbols should prefer same-sector symbols")
    if "NVDA" not in fallback_stock_thesis(symbol="NVDA", overview=overview, news_items=news_items):
        raise AssertionError("fallback stock thesis should mention symbol")

    filtered_series = slice_history_series(
        series=series,
        range_value="1m",
        from_date=None,
        to_date=None,
    )
    turning_points = [{"date": filtered_series[0]["date"], "move": 4.2, "sourceRefIds": ["series-ref"]}]
    timeline = build_history_event_timeline(
        symbol="NVDA",
        news_items=news_items,
        turning_points=turning_points,
        filtered_series=filtered_series,
        tone_from_sentiment_label=tone,
    )
    move_reasons = build_history_move_reasons(turning_points, "series-ref")
    overlaps = build_history_overlaps(filtered_series, turning_points, "series-ref")
    event_markers = build_history_event_markers(timeline)
    ranges = history_available_ranges()
    range_label = history_range_label(
        price_series=build_price_series(filtered_series, limit=len(filtered_series)),
        from_date=None,
        to_date=None,
    )

    if len(filtered_series) != 22:
        raise AssertionError("history slice should honor 1m range")
    if not timeline or not move_reasons or not overlaps or not event_markers:
        raise AssertionError("history builders should produce replay primitives")
    if ranges[0]["value"] != "1m" or "~" not in range_label:
        raise AssertionError("history range helpers should produce expected labels")

    print("stock/history builder tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
