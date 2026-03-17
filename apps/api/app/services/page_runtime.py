from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptLoader
from app.services.schema_validator import PayloadSchemaValidationError
from app.services.schema_validator import JsonSchemaValidator

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


async def build_page_response(
    *,
    page_key: str,
    response_model: type[ResponseModelT],
    prompt_loader: PromptLoader,
    validator: JsonSchemaValidator,
    provider_call: Callable[..., Awaitable[dict[str, Any]]],
    **provider_kwargs: Any,
) -> ResponseModelT:
    prompt_bundle = prompt_loader.load_page(page_key)
    try:
        payload = await provider_call(prompt_bundle=prompt_bundle, **provider_kwargs)
        validator.validate(
            page_key=page_key, schema=prompt_bundle.output_schema, payload=payload
        )
        return response_model.model_validate(payload)
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PayloadSchemaValidationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
