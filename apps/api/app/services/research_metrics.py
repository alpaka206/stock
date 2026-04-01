from __future__ import annotations

from statistics import mean, pstdev


def percent_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def simple_return(series: list[dict], offset: int) -> float:
    if len(series) <= offset:
        return 0.0
    return percent_change(series[0]["close"], series[offset]["close"])


def average_volume(series: list[dict], days: int = 20) -> float:
    window = [row["volume"] for row in series[1 : days + 1]]
    if not window:
        return 0.0
    return round(mean(window), 2)


def volume_ratio(series: list[dict], days: int = 20) -> float:
    baseline = average_volume(series, days)
    if baseline == 0:
        return 0.0
    return round(series[0]["volume"] / baseline, 2)


def volatility(series: list[dict], days: int = 20) -> float:
    closes = [row["close"] for row in series[: days + 1]]
    if len(closes) < 3:
        return 0.0
    returns = [
        percent_change(closes[index], closes[index + 1]) for index in range(len(closes) - 1)
    ]
    return round(pstdev(returns), 2)


def compute_watchlist_score(series: list[dict], sentiment_score: float) -> float:
    score = 55.0
    score += simple_return(series, 5) * 0.55
    score += simple_return(series, 20) * 0.35
    score += (volume_ratio(series) - 1.0) * 12
    score += sentiment_score * 8
    score -= volatility(series) * 0.35
    return round(max(0.0, min(score, 100.0)), 1)


def compute_stock_score(series: list[dict], sentiment_score: float) -> dict:
    technical = max(
        0.0,
        min(
            100.0,
            50.0 + simple_return(series, 20) * 0.8 + (volume_ratio(series) - 1.0) * 10,
        ),
    )
    flow = max(0.0, min(100.0, 45.0 + sentiment_score * 10 + volume_ratio(series) * 8))
    catalyst = max(0.0, min(100.0, 48.0 + sentiment_score * 16 + simple_return(series, 5) * 0.6))
    risk = max(
        0.0,
        min(100.0, 72.0 - volatility(series) * 1.5 - max(-simple_return(series, 5), 0) * 1.5),
    )
    total = round((technical + flow + catalyst + risk) / 4, 1)
    return {
        "total": total,
        "breakdown": {
            "technical": round(technical, 1),
            "flow": round(flow, 1),
            "catalyst": round(catalyst, 1),
            "risk": round(risk, 1),
        },
    }


def identify_turning_points(series: list[dict], limit: int = 3) -> list[dict]:
    candidates: list[dict] = []
    for index in range(len(series) - 1):
        current = series[index]
        previous = series[index + 1]
        move = percent_change(current["close"], previous["close"])
        candidates.append({"date": current["date"], "move": move, "close": current["close"]})

    sorted_candidates = sorted(candidates, key=lambda item: abs(item["move"]), reverse=True)
    return sorted_candidates[:limit]
