from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.prompt_loader import PromptBundle
from app.services.providers.base import ResearchProvider


def _base_source_ref() -> dict[str, str]:
    return {
        "id": "mock-source",
        "title": "개발용 mock provider",
        "kind": "mock",
        "publisher": "stock-workspace",
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "url": "",
        "sourceKey": "mock::provider",
        "symbol": "",
    }


def _sourced_text(text: str) -> dict[str, Any]:
    return {"text": text, "sourceRefIds": ["mock-source"]}


def _base_envelope() -> dict[str, Any]:
    return {
        "asOf": datetime.now(timezone.utc).isoformat(),
        "sourceRefs": [_base_source_ref()],
        "missingData": [],
        "confidence": {
            "score": 0.68,
            "label": "medium",
            "rationale": "개발용 fixture 기반 응답이라 실제 시장 데이터와는 차이가 있을 수 있습니다.",
        },
    }


class MockResearchProvider(ResearchProvider):
    async def get_overview(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        payload = _base_envelope()
        payload.update(
            {
                "benchmarkSnapshot": [
                    {
                        "label": "S&P 500",
                        "symbol": "SPY",
                        "category": "시장 벤치마크",
                        "value": 548.12,
                        "changePercent": 0.64,
                        "note": "S&P 500 ETF 기준입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "NASDAQ 100",
                        "symbol": "QQQ",
                        "category": "시장 벤치마크",
                        "value": 498.44,
                        "changePercent": 1.28,
                        "note": "나스닥 100 ETF 기준입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "반도체",
                        "symbol": "SMH",
                        "category": "섹터 벤치마크",
                        "value": 271.85,
                        "changePercent": 2.14,
                        "note": "반도체 ETF 기준입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "미국 10년물 금리",
                        "symbol": "US10Y",
                        "category": "금리",
                        "value": 4.18,
                        "changePercent": -0.36,
                        "note": "장기 금리 민감도를 보는 기준입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "marketSummary": _sourced_text(
                    "대형 기술주 중심 강세가 이어지지만 금리 민감 구간에서는 섹터 간 확산 여부를 같이 봐야 합니다."
                ),
                "drivers": [
                    _sourced_text("반도체 실적 기대와 AI 투자 확대가 시장을 주도합니다."),
                    _sourced_text("전력 인프라와 냉각 설비까지 관심이 확산되는 구간입니다."),
                ],
                "risks": [
                    _sourced_text("매크로 이벤트 직후 변동성 확대 가능성을 열어 둬야 합니다."),
                    _sourced_text("강세가 소수 섹터에 집중되면 추격 매수 리스크가 커집니다."),
                ],
                "sectorStrength": [
                    {
                        "sector": "반도체",
                        "score": 88,
                        "summary": "실적 기대와 AI 투자 확대가 동시에 지지합니다.",
                        "changePercent": 2.14,
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "score": 79,
                        "summary": "데이터센터 증설이 전력/냉각 수요로 이어집니다.",
                        "changePercent": 1.47,
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "notableNews": [
                    {
                        "headline": "AI 투자 확대 기대가 반도체 강세를 이끌었습니다.",
                        "source": "mock",
                        "summary": "GPU와 메모리 공급망으로 자금이 다시 모이는 흐름입니다.",
                        "impact": "긍정",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "headline": "장기 금리 안정으로 성장주 밸류 부담이 일부 완화됐습니다.",
                        "source": "mock",
                        "summary": "금리 부담이 완화되면서 대형 성장주로 수급이 다시 붙고 있습니다.",
                        "impact": "중립",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
            }
        )
        return payload

    async def get_radar(self, *, prompt_bundle: PromptBundle) -> dict[str, Any]:
        payload = _base_envelope()
        payload.update(
            {
                "selectedSectorSummary": _sourced_text(
                    "반도체와 전력 인프라가 동시에 강한 날이라 리더 종목과 2차 수혜주를 같이 보는 구간입니다. 다만 이벤트 기대가 과열로 바뀌는지 거래량과 일정도 함께 확인해야 합니다."
                ),
                "folderTree": [
                    {
                        "id": "all",
                        "label": "전체 워치리스트",
                        "count": 5,
                        "description": "오늘 우선 검토 중인 종목 전체",
                        "tags": ["오늘", "전체"],
                        "children": [],
                    },
                    {
                        "id": "ai-infra",
                        "label": "AI 인프라",
                        "count": 3,
                        "description": "반도체와 전력 인프라 리더",
                        "tags": ["AI", "인프라"],
                        "children": [],
                    },
                ],
                "watchlistRows": [
                    {
                        "symbol": "NVDA",
                        "name": "NVIDIA",
                        "securityCode": "NV-001",
                        "sector": "반도체",
                        "folderId": "ai-infra",
                        "tags": ["AI", "리더"],
                        "price": 923.42,
                        "changePercent": 2.16,
                        "volumeRatio": 1.42,
                        "relativeStrength": 94,
                        "score": 92,
                        "nextEvent": "GTC 체크",
                        "thesis": "AI 서버 CAPEX 확대의 직접 수혜다.",
                        "condition": "우선 검토",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "AVGO",
                        "name": "Broadcom",
                        "securityCode": "AV-002",
                        "sector": "반도체",
                        "folderId": "ai-infra",
                        "tags": ["네트워크", "AI"],
                        "price": 1345.88,
                        "changePercent": 1.34,
                        "volumeRatio": 1.18,
                        "relativeStrength": 88,
                        "score": 86,
                        "nextEvent": "실적 체크",
                        "thesis": "네트워크와 커스텀 칩이 동시에 살아 있다.",
                        "condition": "관심",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "VRT",
                        "name": "Vertiv",
                        "securityCode": "VR-003",
                        "sector": "전력 인프라",
                        "folderId": "ai-infra",
                        "tags": ["전력", "병목"],
                        "price": 101.12,
                        "changePercent": 2.82,
                        "volumeRatio": 1.67,
                        "relativeStrength": 91,
                        "score": 84,
                        "nextEvent": "전력 설비 체크",
                        "thesis": "데이터센터 전력 병목의 2차 수혜다.",
                        "condition": "우선 검토",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "CRWD",
                        "name": "CrowdStrike",
                        "securityCode": "CR-007",
                        "sector": "사이버보안",
                        "folderId": "all",
                        "tags": ["보안", "리더"],
                        "price": 389.41,
                        "changePercent": 1.55,
                        "volumeRatio": 1.27,
                        "relativeStrength": 86,
                        "score": 82,
                        "nextEvent": "실적 3주 전",
                        "thesis": "방어적 성장 성격이 강한 보안 리더다.",
                        "condition": "우선 검토",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "MSFT",
                        "name": "Microsoft",
                        "securityCode": "MS-008",
                        "sector": "플랫폼 소프트웨어",
                        "folderId": "all",
                        "tags": ["클라우드", "대형주"],
                        "price": 468.60,
                        "changePercent": 0.52,
                        "volumeRatio": 0.88,
                        "relativeStrength": 79,
                        "score": 74,
                        "nextEvent": "클라우드 사용률 체크",
                        "thesis": "AI 수요는 좋지만 밸류 부담을 같이 봐야 한다.",
                        "condition": "조건부 강세",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "sectorCards": [
                    {
                        "sector": "반도체",
                        "score": 88,
                        "thesis": "실적과 CAPEX가 동시에 받쳐 주는 핵심 섹터입니다.",
                        "catalyst": "패키징 병목 완화와 서버 증설",
                        "topPick": "NVDA",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "score": 81,
                        "thesis": "AI 투자 확대가 전력 병목 수요로 번지는 구간입니다.",
                        "catalyst": "전력 설비 수주와 냉각 인프라 확장",
                        "topPick": "VRT",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "brokerReports": [
                    {
                        "sector": "반도체",
                        "house": "Broker A",
                        "symbol": "NVDA",
                        "stance": "비중 확대 유지",
                        "summary": "실적 가시성과 상대강도가 동시에 높은 종목으로 분류합니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "house": "Broker C",
                        "symbol": "VRT",
                        "stance": "우선 검토 상향",
                        "summary": "전력 병목 수혜가 수주로 이어지는지 확인하는 구간입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "keySchedule": [
                    {
                        "sector": "반도체",
                        "time": "09:10",
                        "title": "개장 체크",
                        "note": "NVDA, AVGO 거래량 확인",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "time": "14:00",
                        "title": "전력 설비 메모",
                        "note": "VRT 수주 흐름 확인",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "keyIssues": [
                    {
                        "headline": "전력 병목 이슈가 반도체에서 인프라로 확산",
                        "summary": "핵심 리더뿐 아니라 전력/냉각 인프라 쪽으로 관심이 번지는 흐름입니다.",
                        "impact": "긍정",
                        "sector": "전력 인프라",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "topPicks": [
                    {
                        "sector": "반도체",
                        "symbol": "NVDA",
                        "reason": "실적 가시성과 상대강도가 동시에 높습니다.",
                        "score": 92,
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "symbol": "VRT",
                        "reason": "전력 병목 수혜 논리가 가장 직접적입니다.",
                        "score": 84,
                        "sourceRefIds": ["mock-source"],
                    },
                ],
            }
        )
        return payload

    async def get_stock_detail(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        target = symbol.upper()
        payload = _base_envelope()
        payload.update(
            {
                "instrument": {
                    "symbol": target,
                    "name": "NVIDIA" if target == "NVDA" else f"{target} Sample",
                    "exchange": "NASDAQ",
                    "securityCode": "NV-001" if target == "NVDA" else f"{target}-000",
                    "sector": "반도체",
                    "marketCap": "2.28T",
                },
                "latestPrice": 923.42,
                "changePercent": 2.16,
                "thesis": "실적과 이벤트가 동시에 지지하는 리더 종목이지만, 과열 구간에서는 지지선 유지와 거래량을 함께 봐야 합니다.",
                "priceSeries": [
                    {"date": "2026-02-12", "label": "02/12", "close": 842, "volume": 44},
                    {"date": "2026-02-19", "label": "02/19", "close": 851, "volume": 39},
                    {"date": "2026-02-26", "label": "02/26", "close": 865, "volume": 48},
                    {"date": "2026-03-05", "label": "03/05", "close": 858, "volume": 41},
                    {"date": "2026-03-13", "label": "03/13", "close": 889, "volume": 58},
                    {"date": "2026-03-21", "label": "03/21", "close": 923, "volume": 57},
                ],
                "eventMarkers": [
                    {
                        "id": "earnings",
                        "label": "실적",
                        "tone": "positive",
                        "date": "2026-03-13",
                        "pointLabel": "",
                        "title": "실적과 가이던스 상향",
                        "detail": "데이터센터 매출과 가이던스가 모두 상향됐습니다.",
                        "href": "",
                    }
                ],
                "indicatorGuides": [
                    {
                        "id": "support",
                        "label": "지지 구간",
                        "value": 889,
                        "tone": "positive",
                        "description": "최근 돌파 구간이 방어선 역할을 하는지 확인합니다.",
                        "enabled": True,
                    },
                    {
                        "id": "trend-base",
                        "label": "추세 기준선",
                        "value": 901,
                        "tone": "neutral",
                        "description": "추세 유지 판단 기준선입니다.",
                        "enabled": True,
                    },
                ],
                "rulePresetDefinitions": [
                    {
                        "id": "support-hold",
                        "label": "지지선 유지",
                        "description": "889 위 지지 여부를 봅니다.",
                        "enabledByDefault": True,
                        "tone": "positive",
                    },
                    {
                        "id": "trend-base",
                        "label": "추세선 회복",
                        "description": "20일 기준선 위 종가 유지 여부를 확인합니다.",
                        "enabledByDefault": True,
                        "tone": "neutral",
                    },
                    {
                        "id": "volume-spike",
                        "label": "거래량 배수",
                        "description": "거래량이 추세를 지지하는지 확인합니다.",
                        "enabledByDefault": True,
                        "tone": "positive",
                    },
                ],
                "scoreSummary": {
                    "total": 86,
                    "confidence": {
                        "score": 0.81,
                        "label": "high",
                        "rationale": "가격, 거래량, 이벤트가 같은 방향을 가리킵니다.",
                    },
                    "breakdown": [
                        {
                            "label": "기술 추세",
                            "score": 90,
                            "summary": "상승 추세와 지지선 유지가 아직 유효합니다.",
                        },
                        {
                            "label": "수급/유동성",
                            "score": 84,
                            "summary": "거래량이 붙는 구간이 반복됩니다.",
                        },
                        {
                            "label": "촉매/이슈",
                            "score": 92,
                            "summary": "실적과 행사 이벤트가 동시에 지지합니다.",
                        },
                        {
                            "label": "리스크 관리",
                            "score": 77,
                            "summary": "과열 구간 여부는 계속 체크해야 합니다.",
                        },
                    ],
                },
                "flowMetrics": [
                    {
                        "label": "수급 메모",
                        "value": "준비 중",
                        "detail": "실제 수급 provider 연결 전 개발용 상태입니다.",
                        "tone": "neutral",
                    }
                ],
                "flowUnavailable": {
                    "label": "수급 데이터 준비 중",
                    "reason": "기관/개인/외국인 수급 source를 아직 연결하지 않았습니다.",
                    "expectedSource": "flow provider",
                },
                "optionsShortMetrics": [
                    {
                        "label": "옵션/공매도 메모",
                        "value": "준비 중",
                        "detail": "실제 비율 데이터는 미연결 상태입니다.",
                        "tone": "neutral",
                    }
                ],
                "optionsUnavailable": {
                    "label": "공매도/옵션 데이터 준비 중",
                    "reason": "실제 옵션/공매도 provider를 아직 연결하지 않았습니다.",
                    "expectedSource": "options-short provider",
                },
                "issueCards": [
                    {
                        "title": "실적 상향 유지",
                        "source": "mock",
                        "summary": "실적 발표 후 가이던스 상향이 추세를 지지합니다.",
                        "tone": "positive",
                        "category": "종목",
                        "href": "/history?symbol=NVDA",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "relatedSymbols": ["AVGO", "AMD", "VRT"],
            }
        )
        payload["rulePresetDefinitions"] = [
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
                "guideIds": ["volume-spike"],
                "controlsEventMarkers": False,
            },
        ]
        return payload

    async def get_history(
        self,
        *,
        symbol: str | None,
        range: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        prompt_bundle: PromptBundle,
    ) -> dict[str, Any]:
        target = (symbol or "NVDA").upper()
        payload = _base_envelope()
        payload.update(
            {
                "symbol": target,
                "rangeLabel": f"{from_date or '2025-10-01'} ~ {to_date or '2026-03-21'}",
                "availableRanges": [
                    {"value": "1m", "label": "1개월"},
                    {"value": "3m", "label": "3개월"},
                    {"value": "6m", "label": "6개월"},
                    {"value": "event", "label": "이벤트 구간"},
                ],
                "priceSeries": [
                    {"date": "2025-10-01", "label": "10/01", "close": 612, "volume": 38},
                    {"date": "2025-10-22", "label": "10/22", "close": 648, "volume": 42},
                    {"date": "2025-11-12", "label": "11/12", "close": 701, "volume": 47},
                    {"date": "2025-12-24", "label": "12/24", "close": 718, "volume": 36},
                    {"date": "2026-01-14", "label": "01/14", "close": 782, "volume": 58},
                    {"date": "2026-03-21", "label": "03/21", "close": 923, "volume": 57},
                ],
                "eventMarkers": [
                    {
                        "id": "history-event-1",
                        "label": "섹터",
                        "tone": "positive",
                        "date": "2025-10-22",
                        "pointLabel": "",
                        "title": "AI 서버 투자 확대",
                        "detail": "공급망 메모와 증설 뉴스가 겹치며 리더가 강화됐습니다.",
                        "href": "",
                    },
                    {
                        "id": "history-event-2",
                        "label": "매크로",
                        "tone": "negative",
                        "date": "2025-12-24",
                        "pointLabel": "",
                        "title": "장기 금리 급반등",
                        "detail": "성장주 밸류 부담이 커지며 조정이 나왔습니다.",
                        "href": "",
                    },
                ],
                "eventTimeline": [
                    {
                        "id": "history-event-1",
                        "date": "2025-10-22",
                        "title": "AI 서버 투자 확대",
                        "category": "섹터",
                        "summary": "증설 뉴스와 공급망 메모가 같이 나오며 자금이 리더로 몰렸습니다.",
                        "reaction": "3주 +11%",
                        "tone": "positive",
                        "source": "mock",
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "id": "history-event-2",
                        "date": "2025-12-24",
                        "title": "장기 금리 급반등",
                        "category": "매크로",
                        "summary": "밸류 부담이 커지며 단기 조정 구간이 나타났습니다.",
                        "reaction": "2주 -6%",
                        "tone": "negative",
                        "source": "mock",
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "moveSummary": _sourced_text(
                    f"{target}의 강한 상승 구간은 실적 상향과 AI 인프라 투자 확대가 겹친 결과였고, 조정 구간은 장기 금리 반등에 따른 밸류 부담이 주요 원인이었습니다."
                ),
                "moveReasons": [
                    {
                        "label": "급등 구간 핵심 이유",
                        "description": "실적 가이던스 상향과 CAPEX 확대가 동시에 작동했습니다.",
                        "tone": "positive",
                        "relatedDate": "2026-01-14",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "조정 구간 핵심 이유",
                        "description": "장기 금리 급반등으로 성장주 밸류 부담이 커졌습니다.",
                        "tone": "negative",
                        "relatedDate": "2025-12-24",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "overlappingIndicators": [
                    {
                        "label": "거래량 + 상대강도 중첩",
                        "detail": "실적 이후 거래량과 상대강도가 동시에 강해졌습니다.",
                        "tone": "positive",
                        "relatedDate": "2026-01-14",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "금리 + 밸류 부담",
                        "detail": "금리 반등 시 성장주 밸류 부담이 가격에 바로 반영됐습니다.",
                        "tone": "negative",
                        "relatedDate": "2025-12-24",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "analogsOrPatterns": [
                    _sourced_text("실적 이후 거래량 동반 추세 강화 패턴"),
                    _sourced_text("금리 급등 시 밸류 부담 재부각 패턴"),
                ],
            }
        )
        return payload
