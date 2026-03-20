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
            "rationale": "개발용 fixture 기반 응답이라 실제 시장 데이터보다 신뢰도가 낮습니다.",
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
                        "category": "시장 프록시",
                        "value": 548.12,
                        "changePercent": 0.64,
                        "note": "S&P 500 프록시 ETF 기준 흐름입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "NASDAQ 100",
                        "symbol": "QQQ",
                        "category": "시장 프록시",
                        "value": 498.44,
                        "changePercent": 1.28,
                        "note": "대형 기술주 중심 프록시 ETF 흐름입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "반도체",
                        "symbol": "SMH",
                        "category": "섹터 프록시",
                        "value": 271.85,
                        "changePercent": 2.14,
                        "note": "반도체 섹터 프록시 ETF 기준입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "label": "미국 10년물 금리",
                        "symbol": "US10Y",
                        "category": "금리",
                        "value": 4.18,
                        "changePercent": -0.36,
                        "note": "장기 금리 민감도를 보는 기준 값입니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "marketSummary": _sourced_text(
                    "대형 기술주 중심 강세가 유지되지만 금리 민감 구간에서는 선별 흐름이 나타납니다."
                ),
                "drivers": [
                    _sourced_text("반도체 실적 기대가 지수 상단을 지지합니다."),
                    _sourced_text("장중 금리 안정이 성장주 밸류 부담을 일부 완화했습니다."),
                ],
                "risks": [
                    _sourced_text("매크로 이벤트 전후 변동성 확대 가능성이 남아 있습니다."),
                    _sourced_text("강세가 일부 섹터에만 집중돼 확산력은 제한적입니다."),
                ],
                "sectorStrength": [
                    {
                        "sector": "반도체",
                        "score": 88,
                        "summary": "실적 기대와 AI 투자 모멘텀이 유지됩니다.",
                        "changePercent": 2.14,
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "sector": "전력 인프라",
                        "score": 79,
                        "summary": "데이터센터 투자 확대의 후행 수혜로 해석됩니다.",
                        "changePercent": 1.47,
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "notableNews": [
                    {
                        "headline": "AI 투자 확대 기대가 반도체 강세를 이끌었습니다.",
                        "source": "mock",
                        "summary": "GPU와 메모리 공급망으로 자금이 다시 모이며 상단 리더가 유지되는 흐름입니다.",
                        "impact": "긍정",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "headline": "장중 금리 안정으로 성장주 부담이 일부 완화됐습니다.",
                        "source": "mock",
                        "summary": "장기 금리 부담이 눌리면서 고밸류 성장주 확산 가능성을 다시 점검하는 구간입니다.",
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
                    "반도체와 전력 인프라가 오늘의 우선 검토 섹터입니다."
                ),
                "reportSummary": [
                    _sourced_text("브로커 메모는 대형 반도체의 실적 가시성을 높게 평가합니다."),
                    _sourced_text("전력 인프라는 AI 설비투자의 후행 수혜군으로 분류됩니다."),
                ],
                "keySchedule": [
                    {
                        "time": "09:10",
                        "title": "개장 체크",
                        "note": "반도체 체결 강도 확인",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "time": "14:00",
                        "title": "매크로 브리핑",
                        "note": "금리 민감도 재점검",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "keyIssues": [
                    {
                        "headline": "AI 인프라 수혜군 순환",
                        "summary": "대형 반도체에서 전력과 서버 부품으로 관심이 확산됩니다.",
                        "impact": "긍정",
                        "sourceRefIds": ["mock-source"],
                    }
                ],
                "topPicks": [
                    {
                        "symbol": "NVDA",
                        "reason": "실적 가시성과 상대강도 우위",
                        "score": 92,
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "VRT",
                        "reason": "전력 인프라 후행 수혜",
                        "score": 84,
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "watchlistHighlights": [
                    {
                        "symbol": "NVDA",
                        "thesis": "AI 투자 확대 수혜가 가장 직접적입니다.",
                        "condition": "우선검토",
                        "price": 923.42,
                        "changePercent": 2.16,
                        "score": 92,
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "symbol": "AMD",
                        "thesis": "추격보다 실적 확인이 필요한 구간입니다.",
                        "condition": "조건부 강세",
                        "price": 178.33,
                        "changePercent": 1.04,
                        "score": 73,
                        "sourceRefIds": ["mock-source"],
                    },
                ],
            }
        )
        return payload

    async def get_stock_detail(
        self, *, symbol: str, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        payload = _base_envelope()
        payload.update(
            {
                "score": {
                    "total": 78,
                    "breakdown": {
                        "technical": 26,
                        "flow": 20,
                        "catalyst": 22,
                        "risk": 10,
                    },
                    "sourceRefIds": ["mock-source"],
                },
                "signals": {
                    "positive": [
                        _sourced_text(f"{symbol}은 상대강도가 유지되고 있습니다."),
                        _sourced_text("거래량 확대가 추세 유지에 우호적입니다."),
                    ],
                    "negative": [
                        _sourced_text("단기 과열 구간이라 눌림 없는 추격은 부담입니다."),
                    ],
                },
                "flowSummary": _sourced_text(
                    "기관·외국인 수급은 아직 mock 기준 요약으로만 연결돼 있습니다."
                ),
                "optionsShortSummary": _sourced_text(
                    "공매도와 옵션 데이터는 아직 mock 수준으로만 연결돼 있습니다."
                ),
                "issueSummary": [
                    _sourced_text("실적 이벤트 전 기대가 선반영되고 있습니다."),
                    _sourced_text("섹터 모멘텀이 유지될 때만 점수 유지가 가능합니다."),
                ],
                "chartNotes": {
                    "trend": _sourced_text("중기 상승 추세"),
                    "support": _sourced_text("최근 박스 상단 부근"),
                    "resistance": _sourced_text("직전 고점 부근"),
                },
                "risks": [
                    _sourced_text("실적 이벤트 전후 변동성 확대 가능성"),
                    _sourced_text("금리 반등 시 성장주 밸류 부담 확대"),
                ],
            }
        )
        return payload

    async def get_history(
        self, *, symbol: str | None, prompt_bundle: PromptBundle
    ) -> dict[str, Any]:
        target = symbol or "NVDA"
        payload = _base_envelope()
        payload.update(
            {
                "moveSummary": _sourced_text(
                    f"{target}의 과거 급등 구간을 다시 읽기 위한 mock 리플레이 요약입니다."
                ),
                "turningPoints": [
                    {
                        "date": "2025-11-15",
                        "summary": "실적 발표 이후 거래량이 급증했습니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "date": "2025-11-21",
                        "summary": "섹터 강세 확산과 함께 추세가 가속됐습니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "overlappingIndicators": [
                    {
                        "name": "거래량 증가",
                        "interpretation": "상승 추세 신뢰도가 높아졌습니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "name": "이평선 수렴 후 확산",
                        "interpretation": "변곡점 신호로 읽을 수 있습니다.",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "eventTimelineSummary": [
                    {
                        "date": "2025-11-15",
                        "title": "실적 발표",
                        "source": "mock",
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                    {
                        "date": "2025-11-18",
                        "title": "섹터 뉴스 확산",
                        "source": "mock",
                        "url": "",
                        "sourceRefIds": ["mock-source"],
                    },
                ],
                "analogsOrPatterns": [
                    _sourced_text("실적 이후 거래량 동반 추세 강화 패턴"),
                    _sourced_text("섹터 모멘텀 확산 시 후행 강세 패턴"),
                ],
            }
        )
        return payload
