from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypedDict

from app.services.research_metrics import (
    gap_percent,
    macd,
    moving_average,
    percent_change,
    rsi,
    simple_return,
    volatility,
    volume_ratio,
)


class DailySeriesRow(TypedDict):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class StockNewsItem(TypedDict, total=False):
    title: str
    source: str
    summary: str
    sentimentLabel: str
    tickers: list[str]
    publishedAt: str
    url: str
    sourceRefIds: list[str]


def build_stock_instrument(
    symbol: str,
    overview: Mapping[str, Any],
    *,
    security_code: Callable[[str], str],
    format_market_cap: Callable[[float], str],
) -> dict[str, Any]:
    market_cap = float(overview.get("marketCapitalization", 0.0) or 0.0)
    return {
        "symbol": symbol,
        "name": overview.get("name", symbol),
        "exchange": overview.get("exchange", "") or "NASDAQ",
        "securityCode": security_code(symbol),
        "sector": overview.get("sector", "") or "미분류",
        "marketCap": format_market_cap(market_cap) if market_cap > 0 else "미제공",
    }


def build_price_series(
    series: Sequence[Mapping[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    selected = list(reversed(series[:limit]))
    return [
        {
            "date": str(row["date"]),
            "label": str(row["date"])[5:].replace("-", "/"),
            "close": round(float(row["close"]), 2),
            "volume": round(float(row["volume"]) / 1_000_000, 2),
        }
        for row in selected
    ]


def build_stock_event_markers(
    symbol: str,
    news_items: Sequence[Mapping[str, Any]],
    *,
    tone_from_sentiment_label: Callable[[str], str],
) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{symbol.lower()}-event-{index + 1}",
            "label": "뉴스",
            "tone": tone_from_sentiment_label(str(article.get("sentimentLabel", ""))),
            "date": str(article.get("publishedAt", ""))[:10],
            "pointLabel": "",
            "title": article.get("title", ""),
            "detail": article.get("summary", ""),
            "href": "",
        }
        for index, article in enumerate(news_items[:3])
    ]


def build_stock_indicator_guides(series: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recent = series[:20]
    support = round(min(float(row["low"]) for row in recent), 2)
    resistance = round(max(float(row["high"]) for row in recent), 2)
    trend_base = round(sum(float(row["close"]) for row in recent) / len(recent), 2)
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
            "description": "이벤트 직후 흔들림 가능성을 봅니다.",
            "enabled": False,
        },
    ]


def build_stock_chart_overlays(
    series: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    chronological = list(reversed(series))
    visible = chronological[-limit:]
    visible_dates = {row["date"] for row in visible}
    overlay_specs = [
        (5, "MA 5", "positive"),
        (10, "MA 10", "positive"),
        (20, "MA 20", "neutral"),
        (60, "MA 60", "neutral"),
        (120, "MA 120", "negative"),
    ]
    overlays: list[dict[str, Any]] = []

    for window, label, tone in overlay_specs:
        if len(chronological) < window:
            continue

        points: list[dict[str, Any]] = []
        for index, row in enumerate(chronological):
            if index + 1 < window or row["date"] not in visible_dates:
                continue

            window_rows = chronological[index - window + 1 : index + 1]
            points.append(
                {
                    "date": row["date"],
                    "label": row["date"][5:].replace("-", "/"),
                    "value": round(
                        sum(float(item["close"]) for item in window_rows) / window,
                        2,
                    ),
                }
            )

        if len(points) >= 2:
            overlays.append(
                {
                    "id": f"ma{window}",
                    "label": label,
                    "tone": tone,
                    "points": points,
                    "enabled": window in {5, 20},
                }
            )

    return overlays


def build_stock_technical_metrics(
    series: list[dict[str, Any]],
    source_ref_id: str,
) -> list[dict[str, Any]]:
    latest_close = float(series[0]["close"])
    support = min(float(row["low"]) for row in series[:20])
    resistance = max(float(row["high"]) for row in series[:20])
    ma5 = moving_average(series, 5)
    ma20 = moving_average(series, 20)
    ma60 = moving_average(series, 60)
    ma120 = moving_average(series, 120)
    rsi14 = rsi(series, 14)
    macd_pair = macd(series)
    latest_gap = gap_percent(series)
    volume_multiple = volume_ratio(series)

    trend_detail = _trend_alignment_detail(latest_close, ma5, ma20, ma60, ma120)
    metrics = [
        {
            "id": "ma-alignment",
            "label": "이동평균 배열",
            "value": trend_detail["value"],
            "detail": trend_detail["detail"],
            "tone": trend_detail["tone"],
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "rsi14",
            "label": "RSI 14",
            "value": _format_optional_number(rsi14, suffix=""),
            "detail": _rsi_detail(rsi14),
            "tone": _rsi_tone(rsi14),
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "macd",
            "label": "MACD",
            "value": f"{macd_pair[0]:.2f} / {macd_pair[1]:.2f}" if macd_pair else "데이터 부족",
            "detail": _macd_detail(macd_pair),
            "tone": _macd_tone(macd_pair),
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "volume-ratio",
            "label": "거래량 배수",
            "value": f"{volume_multiple:.2f}x",
            "detail": "최근 거래량을 직전 20거래일 평균과 비교한 값입니다.",
            "tone": "positive" if volume_multiple >= 1.4 else "neutral",
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "support-distance",
            "label": "지지선 거리",
            "value": f"{percent_change(latest_close, support):+.2f}%",
            "detail": f"최근 20거래일 저점 {support:.2f} 대비 현재 종가 위치입니다.",
            "tone": "positive" if latest_close >= support else "negative",
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "resistance-distance",
            "label": "저항선 거리",
            "value": f"{percent_change(latest_close, resistance):+.2f}%",
            "detail": f"최근 20거래일 고점 {resistance:.2f} 대비 돌파 여지를 봅니다.",
            "tone": "positive" if latest_close >= resistance else "neutral",
            "sourceRefIds": [source_ref_id],
        },
    ]

    if latest_gap is not None:
        metrics.append(
            {
                "id": "gap",
                "label": "갭",
                "value": f"{latest_gap:+.2f}%",
                "detail": "당일 시가와 전일 종가 사이의 갭입니다.",
                "tone": "positive" if latest_gap > 1 else "negative" if latest_gap < -1 else "neutral",
                "sourceRefIds": [source_ref_id],
            }
        )

    return metrics


def build_stock_pattern_cards(
    series: list[dict[str, Any]],
    source_ref_id: str,
) -> list[dict[str, Any]]:
    latest_close = float(series[0]["close"])
    recent20 = series[:20]
    recent60 = series[:60] if len(series) >= 60 else series
    high20 = max(float(row["high"]) for row in recent20)
    low20 = min(float(row["low"]) for row in recent20)
    high60 = max(float(row["high"]) for row in recent60)
    low60 = min(float(row["low"]) for row in recent60)
    range20 = (high20 - low20) / latest_close if latest_close else 0
    recovery_from_low60 = percent_change(latest_close, low60)
    distance_from_high60 = percent_change(latest_close, high60)
    ma20 = moving_average(series, 20)
    ma60 = moving_average(series, 60)

    cards = [
        {
            "id": "flat-base",
            "label": "Flat base",
            "similarity": round(max(0.35, min(0.92, 0.88 - range20 * 2)), 2),
            "stage": "박스 상단 확인" if latest_close < high20 else "상단 돌파 시도",
            "invalidation": f"20일 저점 {low20:.2f} 이탈",
            "summary": "최근 20거래일 변동폭이 제한되며 박스권 압축이 진행되는지 확인합니다.",
            "tone": "positive" if range20 <= 0.1 and (ma20 is None or latest_close >= ma20) else "neutral",
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "double-bottom",
            "label": "Double bottom",
            "similarity": round(max(0.25, min(0.86, recovery_from_low60 / 35)), 2),
            "stage": "넥라인 회복 확인" if latest_close < high60 else "넥라인 돌파",
            "invalidation": f"60일 저점 {low60:.2f} 재이탈",
            "summary": "중기 저점 이후 회복 폭과 이전 고점 회복 여부를 함께 봅니다.",
            "tone": "positive" if recovery_from_low60 >= 8 and distance_from_high60 > -8 else "neutral",
            "sourceRefIds": [source_ref_id],
        },
        {
            "id": "ma-trend",
            "label": "MA trend",
            "similarity": _ma_trend_similarity(latest_close, ma20, ma60),
            "stage": "추세 유지" if ma20 and latest_close >= ma20 else "추세 회복 확인",
            "invalidation": f"MA20 {ma20:.2f} 이탈" if ma20 else "MA20 산출 데이터 부족",
            "summary": "현재가가 중기 이동평균 위에서 유지되는지와 MA20/MA60 배열을 함께 확인합니다.",
            "tone": "positive" if ma20 and latest_close >= ma20 and (not ma60 or ma20 >= ma60) else "neutral",
            "sourceRefIds": [source_ref_id],
        },
    ]

    return sorted(cards, key=lambda item: item["similarity"], reverse=True)


def build_stock_rule_preset_definitions() -> list[dict[str, Any]]:
    return [
        {
            "id": "ma-trend",
            "label": "이동평균 추세",
            "description": "MA 5/20/60/120 배열과 현재가 위치를 확인합니다.",
            "enabledByDefault": True,
            "tone": "positive",
            "guideIds": ["ma5", "ma20", "ma60", "ma120"],
            "controlsEventMarkers": False,
        },
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
            "id": "momentum-rsi",
            "label": "RSI 모멘텀",
            "description": "RSI 14 기준 과열/침체와 추세 지속 여부를 확인합니다.",
            "enabledByDefault": True,
            "tone": "neutral",
            "guideIds": [],
            "controlsEventMarkers": False,
        },
        {
            "id": "macd-cross",
            "label": "MACD 교차",
            "description": "MACD와 signal 값 위치로 단기 모멘텀 전환을 확인합니다.",
            "enabledByDefault": False,
            "tone": "neutral",
            "guideIds": [],
            "controlsEventMarkers": False,
        },
        {
            "id": "pattern-similarity",
            "label": "패턴 유사도",
            "description": "Flat base, double bottom 등 현재 차트 구조와의 유사도를 확인합니다.",
            "enabledByDefault": True,
            "tone": "positive",
            "guideIds": [],
            "controlsEventMarkers": False,
        },
        {
            "id": "volatility-guard",
            "label": "변동성 경계",
            "description": "과열 후 흔들림 정도 여부를 경고합니다.",
            "enabledByDefault": False,
            "tone": "negative",
            "guideIds": ["volatility-guard", "volatility"],
            "controlsEventMarkers": False,
        },
        {
            "id": "event-window",
            "label": "이벤트 창 관리",
            "description": "실적과 행사 직전의 이벤트 마커를 확인합니다.",
            "enabledByDefault": True,
            "tone": "neutral",
            "guideIds": [],
            "controlsEventMarkers": True,
        },
    ]


def build_stock_score_summary(score_model: Mapping[str, Any]) -> dict[str, Any]:
    breakdown = score_model["breakdown"]
    return {
        "total": score_model["total"],
        "confidence": {
            "score": 0.78,
            "label": "medium",
            "rationale": "가격, 거래량, 뉴스가 함께 있는 구간이지만 수급/옵션 데이터는 비어 있습니다.",
        },
        "breakdown": [
            {"label": "기술 추세", "score": breakdown["technical"], "summary": "가격과 거래량 기반 기술 추세 점수입니다."},
            {"label": "수급/유동성", "score": breakdown["flow"], "summary": "뉴스 감성과 거래량을 반영한 유동성 점수입니다."},
            {"label": "촉매/이슈", "score": breakdown["catalyst"], "summary": "최근 뉴스와 모멘텀을 반영한 촉매 점수입니다."},
            {"label": "리스크 관리", "score": breakdown["risk"], "summary": "변동성과 하락 구간 민감도를 반영한 리스크 점수입니다."},
        ],
    }


def build_stock_issue_cards(
    symbol: str,
    overview: Mapping[str, Any],
    news_items: Sequence[Mapping[str, Any]],
    *,
    sector_by_symbol: Mapping[str, str],
    tone_from_sentiment_label: Callable[[str], str],
) -> list[dict[str, Any]]:
    sector = str(overview.get("sector", "") or sector_by_symbol.get(symbol, ""))
    issues: list[dict[str, Any]] = []
    for article in news_items[:3]:
        issues.append(
            {
                "title": article.get("title", ""),
                "source": article.get("source", "Alpha Vantage"),
                "summary": article.get("summary", ""),
                "tone": tone_from_sentiment_label(str(article.get("sentimentLabel", ""))),
                "category": "종목" if symbol in article.get("tickers", []) else "시황",
                "href": f"/history?symbol={symbol}",
                "sourceRefIds": list(article.get("sourceRefIds", [])),
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


def build_related_symbols(
    symbol: str,
    sector: str,
    *,
    radar_symbols: Sequence[str],
    sector_by_symbol: Mapping[str, str],
) -> list[str]:
    same_sector = [
        item for item in radar_symbols if item != symbol and sector_by_symbol.get(item, "") == sector
    ]
    fallback = [item for item in radar_symbols if item != symbol]
    return (same_sector or fallback)[:3]


def fallback_stock_thesis(
    *,
    symbol: str,
    overview: Mapping[str, Any],
    news_items: Sequence[Mapping[str, Any]],
) -> str:
    sector = overview.get("sector", "관련 섹터")
    if news_items:
        return f"{symbol}는 {sector} 흐름 속에서 '{news_items[0].get('title', '')}' 이슈를 우선 확인해야 합니다."
    return f"{symbol}는 {sector} 내 가격 추세와 거래량 확인이 필요한 종목입니다."


def _trend_alignment_detail(
    latest_close: float,
    ma5: float | None,
    ma20: float | None,
    ma60: float | None,
    ma120: float | None,
) -> dict[str, str]:
    available = [value for value in [ma5, ma20, ma60, ma120] if value is not None]
    if len(available) < 2:
        return {
            "value": "데이터 부족",
            "detail": "이동평균 배열을 판단할 만큼 긴 시계열이 아직 부족합니다.",
            "tone": "neutral",
        }

    bullish = ma5 is not None and ma20 is not None and ma60 is not None and latest_close >= ma5 >= ma20 >= ma60
    bearish = ma5 is not None and ma20 is not None and ma60 is not None and latest_close <= ma5 <= ma20 <= ma60

    if bullish:
        return {
            "value": "정배열",
            "detail": "현재가가 단기/중기 이동평균 위에 있어 추세 지속을 확인하는 구간입니다.",
            "tone": "positive",
        }
    if bearish:
        return {
            "value": "역배열",
            "detail": "현재가가 주요 이동평균 아래에 있어 회복 확인이 먼저 필요합니다.",
            "tone": "negative",
        }

    return {
        "value": "혼합",
        "detail": "이동평균 배열이 엇갈려 있어 지지선과 거래량 확인이 필요합니다.",
        "tone": "neutral",
    }


def _format_optional_number(value: float | None, *, suffix: str) -> str:
    if value is None:
        return "데이터 부족"
    return f"{value:.1f}{suffix}"


def _rsi_detail(value: float | None) -> str:
    if value is None:
        return "RSI 계산에 필요한 14거래일 이상의 데이터가 부족합니다."
    if value >= 70:
        return "과열권에 가까워 추격보다 눌림 확인이 유리합니다."
    if value <= 30:
        return "침체권에 가까워 반등 시 거래량 동반 여부를 확인합니다."
    return "중립권에서 추세 방향과 거래량을 함께 확인합니다."


def _rsi_tone(value: float | None) -> str:
    if value is None:
        return "neutral"
    if value >= 70:
        return "negative"
    if value <= 30:
        return "positive"
    return "neutral"


def _macd_detail(value: tuple[float, float] | None) -> str:
    if value is None:
        return "MACD 계산에 필요한 35거래일 이상의 데이터가 부족합니다."
    macd_line, signal_line = value
    if macd_line >= signal_line:
        return "MACD가 signal 위에 있어 단기 모멘텀은 양호합니다."
    return "MACD가 signal 아래에 있어 단기 모멘텀 회복 확인이 필요합니다."


def _macd_tone(value: tuple[float, float] | None) -> str:
    if value is None:
        return "neutral"
    return "positive" if value[0] >= value[1] else "negative"


def _ma_trend_similarity(
    latest_close: float,
    ma20: float | None,
    ma60: float | None,
) -> float:
    if ma20 is None:
        return 0.35
    score = 0.55
    if latest_close >= ma20:
        score += 0.2
    if ma60 is not None and ma20 >= ma60:
        score += 0.15
    return round(max(0.2, min(score, 0.92)), 2)
