from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.providers.radar_builders import (  # noqa: E402
    RadarRawRow,
    build_radar_alert_rules,
    build_radar_detected_alerts,
    build_radar_folder_tree,
    build_radar_key_issues,
    build_radar_sector_cards,
    build_radar_top_picks,
    build_radar_watchlist_rows,
)


def main() -> int:
    raw_rows: list[RadarRawRow] = [
        {
            "symbol": "NVDA",
            "sector": "반도체",
            "price": 920.4,
            "changePercent": 2.1,
            "return20d": 8.4,
            "volumeRatio": 1.72,
            "sentimentScore": 0.31,
            "score": 91,
            "condition": "강한 모멘텀",
            "sourceRefIds": ["series-nvda", "sector-map"],
        },
        {
            "symbol": "RISK",
            "sector": "소프트웨어",
            "price": 41.2,
            "changePercent": -3.4,
            "return20d": -7.1,
            "volumeRatio": 0.8,
            "sentimentScore": -0.21,
            "score": 38,
            "condition": "방어 확인",
            "sourceRefIds": ["series-risk", "sector-map"],
        },
    ]
    news_by_symbol = {
        "NVDA": [{"summary": "가속기 수요가 다시 강해졌습니다."}],
    }

    watchlist_rows = build_radar_watchlist_rows(
        raw_rows,
        news_by_symbol,
        instrument_name=lambda symbol: f"{symbol} Inc.",
        security_code=lambda symbol: f"{symbol}-US",
        folder_id=lambda sector, score: "high-conviction" if score >= 80 else sector,
        tags=lambda sector, score: [sector, "고확신" if score >= 80 else "방어"],
        next_event=lambda sector: f"{sector} 체크",
        relative_strength_score=lambda row: round(float(row["return20d"]) * 2, 1),
    )
    if [row["symbol"] for row in watchlist_rows] != ["NVDA", "RISK"]:
        raise AssertionError("watchlist rows should be score-sorted")

    sector_cards = build_radar_sector_cards(
        watchlist_rows,
        sector_catalyst=lambda sector: f"{sector} 촉매",
    )
    top_picks = build_radar_top_picks(sector_cards)
    alerts = build_radar_detected_alerts(watchlist_rows)
    rules = build_radar_alert_rules()
    folder_tree = build_radar_folder_tree(
        watchlist_rows,
        slugify=lambda value: value.lower().replace(" ", "-"),
    )
    key_issues = build_radar_key_issues(
        [{"title": "NVDA headline", "summary": "요약", "sentimentLabel": "Bullish", "tickers": ["NVDA"], "sourceRefIds": ["news"]}],
        sector_by_symbol={"NVDA": "반도체"},
        impact_from_sentiment=lambda value: "긍정" if value else "중립",
    )

    if top_picks[0]["symbol"] != "NVDA":
        raise AssertionError("top pick should follow highest sector score")
    if {alert["ruleId"] for alert in alerts} != {
        "high-conviction-momentum",
        "volume-spike",
        "risk-reversal",
    }:
        raise AssertionError("expected all radar alert rules to trigger in fixture")
    if len(rules) != 3:
        raise AssertionError("expected three radar alert rules")
    if folder_tree[0]["count"] != 2:
        raise AssertionError("folder tree should include all rows")
    if key_issues[0]["sector"] != "반도체":
        raise AssertionError("key issue should resolve sector from primary symbol")

    print("radar builder tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
