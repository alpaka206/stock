from fastapi import APIRouter, Depends

from app.dependencies import get_prompt_loader, get_provider, get_schema_validator
from app.schemas.stocks import StockDetailResponse
from app.services.page_runtime import build_page_response
from app.services.prompt_loader import PromptLoader
from app.services.providers.base import ResearchProvider
from app.services.schema_validator import JsonSchemaValidator

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/{symbol}", response_model=StockDetailResponse)
async def get_stock_detail(
    symbol: str,
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    validator: JsonSchemaValidator = Depends(get_schema_validator),
    provider: ResearchProvider = Depends(get_provider),
) -> StockDetailResponse:
    return await build_page_response(
        page_key="stocks",
        response_model=StockDetailResponse,
        prompt_loader=prompt_loader,
        validator=validator,
        provider_call=provider.get_stock_detail,
        symbol=symbol.upper(),
    )
