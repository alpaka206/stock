from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_provider
from app.schemas.search import InstrumentSearchResponse
from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.providers.base import ResearchProvider

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("/search", response_model=InstrumentSearchResponse)
async def search_instruments(
    q: str = Query(..., min_length=1, max_length=80, description="종목 검색어"),
    limit: int = Query(default=6, ge=1, le=10, description="최대 결과 수"),
    provider: ResearchProvider = Depends(get_provider),
) -> InstrumentSearchResponse:
    try:
        items = await provider.search_instruments(query=q, limit=limit)
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return InstrumentSearchResponse(items=items)
