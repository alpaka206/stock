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


def moving_average(series: list[dict], days: int) -> float | None:
    if len(series) < days:
        return None
    closes = [row["close"] for row in series[:days]]
    return round(mean(closes), 2)


def rsi(series: list[dict], days: int = 14) -> float | None:
    if len(series) <= days:
        return None

    gains: list[float] = []
    losses: list[float] = []
    for index in range(days):
        change = float(series[index]["close"]) - float(series[index + 1]["close"])
        if change >= 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))

    average_gain = mean(gains)
    average_loss = mean(losses)
    if average_loss == 0:
        return 100.0

    relative_strength = average_gain / average_loss
    return round(100 - (100 / (1 + relative_strength)), 1)


def macd(series: list[dict]) -> tuple[float, float] | None:
    if len(series) < 35:
        return None

    closes = [float(row["close"]) for row in reversed(series)]
    macd_line = [_ema(closes, 12)[index] - _ema(closes, 26)[index] for index in range(len(closes))]
    signal_line = _ema(macd_line, 9)
    return round(macd_line[-1], 2), round(signal_line[-1], 2)


def gap_percent(series: list[dict]) -> float | None:
    if len(series) < 2:
        return None
    previous_close = float(series[1]["close"])
    if previous_close == 0:
        return None
    return round(((float(series[0]["open"]) - previous_close) / previous_close) * 100, 2)


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


def _ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []

    multiplier = 2 / (period + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append((value - output[-1]) * multiplier + output[-1])
    return output
