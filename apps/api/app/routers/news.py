from fastapi import APIRouter, Depends

from app.dependencies import get_prompt_loader, get_provider, get_schema_validator
from app.schemas.news import NewsResponse
from app.services.page_runtime import build_page_response
from app.services.prompt_loader import PromptLoader
from app.services.providers.base import ResearchProvider
from app.services.schema_validator import JsonSchemaValidator

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=NewsResponse)
async def get_news(
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    validator: JsonSchemaValidator = Depends(get_schema_validator),
    provider: ResearchProvider = Depends(get_provider),
) -> NewsResponse:
    return await build_page_response(
        page_key="news",
        response_model=NewsResponse,
        prompt_loader=prompt_loader,
        validator=validator,
        provider_call=provider.get_news,
    )
