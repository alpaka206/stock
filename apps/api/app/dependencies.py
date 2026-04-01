from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.prompt_loader import PromptLoader
from app.services.providers.base import ResearchProvider
from app.services.providers.factory import create_provider
from app.services.schema_validator import JsonSchemaValidator


@lru_cache(maxsize=1)
def get_prompt_loader() -> PromptLoader:
    settings = get_settings()
    return PromptLoader(settings.prompt_root)


@lru_cache(maxsize=1)
def get_schema_validator() -> JsonSchemaValidator:
    return JsonSchemaValidator()


@lru_cache(maxsize=1)
def get_provider() -> ResearchProvider:
    settings = get_settings()
    return create_provider(settings.default_provider, settings)
