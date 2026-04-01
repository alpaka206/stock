from fastapi import APIRouter, Depends

from app.dependencies import get_prompt_loader, get_provider, get_schema_validator
from app.schemas.radar import RadarResponse
from app.services.page_runtime import build_page_response
from app.services.prompt_loader import PromptLoader
from app.services.providers.base import ResearchProvider
from app.services.schema_validator import JsonSchemaValidator

router = APIRouter(prefix="/radar", tags=["radar"])


@router.get("", response_model=RadarResponse)
async def get_radar(
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    validator: JsonSchemaValidator = Depends(get_schema_validator),
    provider: ResearchProvider = Depends(get_provider),
) -> RadarResponse:
    return await build_page_response(
        page_key="radar",
        response_model=RadarResponse,
        prompt_loader=prompt_loader,
        validator=validator,
        provider_call=provider.get_radar,
    )
