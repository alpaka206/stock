from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from app.services.research_metrics import volume_ratio, volatility


def slice_history_series(
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


def build_history_event_timeline(
    *,
    symbol: str,
    news_items: Sequence[Mapping[str, Any]],
    turning_points: Sequence[Mapping[str, Any]],
    filtered_series: Sequence[Mapping[str, Any]],
    tone_from_sentiment_label: Callable[[str], str],
) -> list[dict[str, Any]]:
    series_dates = sorted({str(row["date"]) for row in filtered_series if row.get("date")})
    events: list[dict[str, Any]] = []
    for index, turning_point in enumerate(turning_points[:3]):
        move = float(turning_point["move"])
        tone = "positive" if move > 0 else "negative"
        events.append(
            {
                "id": f"{symbol.lower()}-turning-{index + 1}",
                "date": turning_point["date"],
                "title": "가격 변곡점",
                "category": "차트",
                "summary": f"하루 변동폭 {move:.2f}% 구간입니다.",
                "reaction": f"{move:+.2f}%",
                "tone": tone,
                "source": "price-series",
                "url": "",
                "sourceRefIds": list(turning_point.get("sourceRefIds", [])),
            }
        )

    filtered_news: list[tuple[Mapping[str, Any], str]] = []
    for article in news_items:
        aligned_date = align_history_event_date(
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
                "tone": tone_from_sentiment_label(str(article.get("sentimentLabel", ""))),
                "source": article.get("source", "Alpha Vantage"),
                "url": article.get("url", ""),
                "sourceRefIds": list(article.get("sourceRefIds", [])),
            }
        )

    events.sort(key=lambda item: item["date"])
    return events


def align_history_event_date(event_date: str, series_dates: Sequence[str]) -> str | None:
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


def build_history_move_reasons(
    turning_points: Sequence[Mapping[str, Any]],
    source_ref_id: str,
) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for turning_point in turning_points[:3]:
        move = float(turning_point["move"])
        tone = "positive" if move > 0 else "negative"
        reasons.append(
            {
                "label": "급등 구간 핵심 이유" if tone == "positive" else "조정 구간 핵심 이유",
                "description": f"{turning_point['date']} 전후 가격 변동이 {move:+.2f}%로 커졌습니다.",
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


def build_history_overlaps(
    series: list[dict[str, Any]],
    turning_points: Sequence[Mapping[str, Any]],
    source_ref_id: str,
) -> list[dict[str, Any]]:
    overlap_items: list[dict[str, Any]] = []
    if turning_points:
        first_move = float(turning_points[0]["move"])
        overlap_items.append(
            {
                "label": "거래량 + 변동성 중첩",
                "detail": f"최근 변곡점 구간의 변동성은 {volatility(series):.2f} 수준입니다.",
                "tone": "positive" if first_move > 0 else "negative",
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


def build_history_event_markers(event_timeline: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
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


def history_available_ranges() -> list[dict[str, str]]:
    return [
        {"value": "1m", "label": "1개월"},
        {"value": "3m", "label": "3개월"},
        {"value": "6m", "label": "6개월"},
        {"value": "event", "label": "이벤트 중심"},
    ]


def history_range_label(
    *,
    price_series: Sequence[Mapping[str, Any]],
    from_date: str | None,
    to_date: str | None,
) -> str:
    if from_date or to_date:
        return f"{from_date or '시작'} ~ {to_date or '현재'}"
    if not price_series:
        return "데이터 없음"
    return f"{price_series[0]['date']} ~ {price_series[-1]['date']}"


def fallback_history_summary(move_reasons: Sequence[Mapping[str, Any]]) -> str:
    if not move_reasons:
        return "유효한 가격 변동 이벤트가 부족합니다."
    return str(move_reasons[0]["description"])
