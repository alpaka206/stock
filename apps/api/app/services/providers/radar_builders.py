from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, NotRequired, TypedDict


class RadarRawRow(TypedDict):
    symbol: str
    sector: str
    price: float
    changePercent: float
    return20d: float
    volumeRatio: float
    sentimentScore: float
    score: float
    condition: str
    sourceRefIds: list[str]


class RadarNewsItem(TypedDict, total=False):
    title: str
    summary: str
    sentimentLabel: str
    tickers: list[str]
    sourceRefIds: list[str]


class RadarWatchlistRow(TypedDict):
    symbol: str
    name: str
    securityCode: str
    sector: str
    folderId: str
    tags: list[str]
    price: float
    changePercent: float
    volumeRatio: float
    relativeStrength: float
    score: float
    nextEvent: str
    thesis: str
    condition: str
    sourceRefIds: list[str]


class RadarSectorCard(TypedDict):
    sector: str
    score: float
    thesis: str
    catalyst: str
    topPick: str
    sourceRefIds: list[str]


class RadarBrokerReport(TypedDict):
    sector: str
    house: str
    symbol: str
    stance: str
    summary: str
    sourceRefIds: list[str]


class RadarScheduleItem(TypedDict):
    sector: str
    time: str
    title: str
    note: str
    sourceRefIds: list[str]


class RadarKeyIssue(TypedDict):
    headline: str
    summary: str
    impact: str
    sector: str
    sourceRefIds: list[str]


class RadarTopPick(TypedDict):
    sector: str
    symbol: str
    reason: str
    score: float
    sourceRefIds: list[str]


class RadarAlertRule(TypedDict):
    id: str
    label: str
    description: str
    severity: str
    enabledByDefault: bool


class RadarDetectedAlert(TypedDict):
    id: str
    ruleId: str
    symbol: str
    title: str
    summary: str
    severity: str
    tone: str
    triggeredAt: str
    sourceRefIds: list[str]


class RadarFolderNode(TypedDict):
    id: str
    label: str
    count: int
    description: str
    tags: list[str]
    children: NotRequired[list["RadarFolderNode"]]


def build_radar_watchlist_rows(
    rows: Sequence[RadarRawRow],
    news_by_symbol: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    instrument_name: Callable[[str], str],
    security_code: Callable[[str], str],
    folder_id: Callable[[str, float], str],
    tags: Callable[[str, float], list[str]],
    next_event: Callable[[str], str],
    relative_strength_score: Callable[[Mapping[str, Any]], float],
) -> list[RadarWatchlistRow]:
    ordered = sorted(rows, key=lambda item: item["score"], reverse=True)
    hydrated: list[RadarWatchlistRow] = []
    for row in ordered:
        symbol = row["symbol"]
        sector = row["sector"]
        top_news = news_by_symbol.get(symbol, [])
        thesis = (
            str(top_news[0].get("summary", ""))
            if top_news
            else f"{sector} 내 상대 강도 상위 종목입니다."
        )
        hydrated.append(
            {
                "symbol": symbol,
                "name": instrument_name(symbol),
                "securityCode": security_code(symbol),
                "sector": sector,
                "folderId": folder_id(sector, row["score"]),
                "tags": tags(sector, row["score"]),
                "price": row["price"],
                "changePercent": row["changePercent"],
                "volumeRatio": row["volumeRatio"],
                "relativeStrength": relative_strength_score(row),
                "score": row["score"],
                "nextEvent": next_event(sector),
                "thesis": thesis,
                "condition": row["condition"],
                "sourceRefIds": row["sourceRefIds"],
            }
        )
    return hydrated


def build_radar_sector_cards(
    rows: Sequence[RadarWatchlistRow],
    *,
    sector_catalyst: Callable[[str], str],
) -> list[RadarSectorCard]:
    grouped: dict[str, list[RadarWatchlistRow]] = {}
    for row in rows:
        grouped.setdefault(row["sector"], []).append(row)

    cards: list[RadarSectorCard] = []
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
                "catalyst": sector_catalyst(sector),
                "topPick": top_row["symbol"],
                "sourceRefIds": top_row["sourceRefIds"],
            }
        )

    cards.sort(key=lambda item: item["score"], reverse=True)
    return cards


def build_radar_broker_reports(
    sector_cards: Sequence[RadarSectorCard],
) -> list[RadarBrokerReport]:
    reports: list[RadarBrokerReport] = []
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


def build_radar_schedule(
    sector_cards: Sequence[RadarSectorCard],
) -> list[RadarScheduleItem]:
    schedule_times = ["09:10", "11:20", "14:00"]
    items: list[RadarScheduleItem] = []
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


def build_radar_key_issues(
    news_items: Sequence[Mapping[str, Any]],
    *,
    sector_by_symbol: Mapping[str, str],
    impact_from_sentiment: Callable[[str], str],
) -> list[RadarKeyIssue]:
    issues: list[RadarKeyIssue] = []
    for article in news_items[:3]:
        tickers = article.get("tickers", [])
        primary_symbol = str(tickers[0]) if tickers else ""
        issues.append(
            {
                "headline": str(article.get("title", "")),
                "summary": str(article.get("summary", "")),
                "impact": impact_from_sentiment(str(article.get("sentimentLabel", ""))),
                "sector": sector_by_symbol.get(primary_symbol, ""),
                "sourceRefIds": list(article.get("sourceRefIds", [])),
            }
        )
    return issues


def build_radar_top_picks(
    sector_cards: Sequence[RadarSectorCard],
) -> list[RadarTopPick]:
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


def build_radar_alert_rules() -> list[RadarAlertRule]:
    return [
        {
            "id": "high-conviction-momentum",
            "label": "고확신 모멘텀",
            "description": "점수 80 이상이면서 당일 수익률이 양수인 관심종목을 표시합니다.",
            "severity": "watch",
            "enabledByDefault": True,
        },
        {
            "id": "volume-spike",
            "label": "거래량 급증",
            "description": "최근 평균 대비 거래량 배수가 1.5배 이상인 종목을 표시합니다.",
            "severity": "info",
            "enabledByDefault": True,
        },
        {
            "id": "risk-reversal",
            "label": "리스크 반전",
            "description": "점수 45 미만 또는 당일 -3% 이하 하락 종목을 표시합니다.",
            "severity": "critical",
            "enabledByDefault": True,
        },
    ]


def build_radar_detected_alerts(
    rows: Sequence[RadarWatchlistRow],
) -> list[RadarDetectedAlert]:
    triggered_at = datetime.now(timezone.utc).isoformat()
    alerts: list[RadarDetectedAlert] = []
    for row in rows:
        source_ref_ids = row.get("sourceRefIds", [])
        if row.get("score", 0) >= 80 and row.get("changePercent", 0) > 0:
            alerts.append(
                {
                    "id": f"{row['symbol'].lower()}-high-conviction-momentum",
                    "ruleId": "high-conviction-momentum",
                    "symbol": row["symbol"],
                    "title": f"{row['symbol']} 고확신 모멘텀",
                    "summary": f"점수 {row.get('score', 0):.0f}, 등락률 {row.get('changePercent', 0):+.2f}%로 우선 확인 대상입니다.",
                    "severity": "watch",
                    "tone": "positive",
                    "triggeredAt": triggered_at,
                    "sourceRefIds": source_ref_ids,
                }
            )
        if row.get("volumeRatio", 0) >= 1.5:
            alerts.append(
                {
                    "id": f"{row['symbol'].lower()}-volume-spike",
                    "ruleId": "volume-spike",
                    "symbol": row["symbol"],
                    "title": f"{row['symbol']} 거래량 급증",
                    "summary": f"거래량 배수가 {row.get('volumeRatio', 0):.2f}x로 평소보다 높습니다.",
                    "severity": "info",
                    "tone": "neutral",
                    "triggeredAt": triggered_at,
                    "sourceRefIds": source_ref_ids,
                }
            )
        if row.get("score", 0) < 45 or row.get("changePercent", 0) <= -3:
            alerts.append(
                {
                    "id": f"{row['symbol'].lower()}-risk-reversal",
                    "ruleId": "risk-reversal",
                    "symbol": row["symbol"],
                    "title": f"{row['symbol']} 리스크 반전",
                    "summary": f"점수 {row.get('score', 0):.0f}, 등락률 {row.get('changePercent', 0):+.2f}%로 방어 확인이 필요합니다.",
                    "severity": "critical",
                    "tone": "negative",
                    "triggeredAt": triggered_at,
                    "sourceRefIds": source_ref_ids,
                }
            )

    return alerts[:8]


def build_radar_folder_tree(
    rows: Sequence[RadarWatchlistRow],
    *,
    slugify: Callable[[str], str],
) -> list[RadarFolderNode]:
    grouped: dict[str, list[RadarWatchlistRow]] = {}
    for row in rows:
        grouped.setdefault(row["sector"], []).append(row)

    children: list[RadarFolderNode] = [
        {
            "id": slugify(sector),
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
