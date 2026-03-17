from fastapi import APIRouter, Depends, Query

from app.dependencies import get_prompt_loader, get_provider, get_schema_validator
from app.schemas.history import HistoryResponse
from app.services.page_runtime import build_page_response
from app.services.prompt_loader import PromptLoader
from app.services.providers.base import ResearchProvider
from app.services.schema_validator import JsonSchemaValidator

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
async def get_history(
    symbol: str | None = Query(default=None, description="종목 심볼"),
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    validator: JsonSchemaValidator = Depends(get_schema_validator),
    provider: ResearchProvider = Depends(get_provider),
) -> HistoryResponse:
    return await build_page_response(
        page_key="history",
        response_model=HistoryResponse,
        prompt_loader=prompt_loader,
        validator=validator,
        provider_call=provider.get_history,
        symbol=symbol.upper() if symbol else None,
    )
