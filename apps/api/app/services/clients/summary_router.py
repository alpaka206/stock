from __future__ import annotations

from typing import Any

from app.services.clients.gemini_responses import GeminiResearchClient
from app.services.clients.openai_responses import OpenAIResearchClient
from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptBundle


class ResearchSummaryClient:
    def __init__(
        self,
        *,
        llm_provider: str,
        openai_api_key: str | None,
        openai_model: str,
        gemini_api_key: str | None,
        gemini_model: str,
        gemini_base_url: str,
        timeout_seconds: float,
    ) -> None:
        self.llm_provider = llm_provider
        self.openai = OpenAIResearchClient(
            api_key=openai_api_key,
            model=openai_model,
        )
        self.gemini = GeminiResearchClient(
            api_key=gemini_api_key,
            model=gemini_model,
            base_url=gemini_base_url,
            timeout_seconds=timeout_seconds,
        )

    def configured_provider_names(self) -> list[str]:
        names: list[str] = []
        if self.openai.is_configured:
            names.append("openai")
        if self.gemini.is_configured:
            names.append("gemini")
        return names

    def has_configured_provider(self) -> bool:
        return bool(self.configured_provider_names())

    async def generate_page_response(
        self,
        *,
        prompt_bundle: PromptBundle,
        page_key: str,
        facts: dict[str, Any],
        source_refs: list[dict[str, Any]],
        missing_data: list[dict[str, str]],
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        providers = self._iter_provider_clients()
        if not providers:
            raise ProviderConfigurationError(
                "?? ??? LLM provider? ?? deterministic fallback?? ?????."
            )

        for provider_name, client in providers:
            try:
                return await client.generate_page_response(
                    prompt_bundle=prompt_bundle,
                    page_key=page_key,
                    facts=facts,
                    source_refs=source_refs,
                    missing_data=missing_data,
                )
            except ProviderConfigurationError as exc:
                last_error = exc
                if self.llm_provider in {"openai", "gemini"}:
                    raise
                continue
            except ExternalServiceError as exc:
                last_error = exc
                if self.llm_provider in {"openai", "gemini"}:
                    raise
                continue

        if isinstance(last_error, Exception):
            raise last_error
        raise ProviderConfigurationError(
            "?? ??? LLM provider? ?? deterministic fallback?? ?????."
        )

    async def probe_health(self) -> dict[str, Any]:
        providers = self._iter_provider_clients()
        if not providers:
            raise ProviderConfigurationError(
                "?? ??? LLM provider? ?? health probe? ?????."
            )

        last_error: Exception | None = None
        for provider_name, client in providers:
            try:
                await client.probe_health()
                return {"ok": True, "provider": provider_name}
            except ProviderConfigurationError as exc:
                last_error = exc
                if self.llm_provider in {"openai", "gemini"}:
                    raise
                continue
            except ExternalServiceError as exc:
                last_error = exc
                if self.llm_provider in {"openai", "gemini"}:
                    raise
                continue

        if isinstance(last_error, Exception):
            raise last_error
        raise ProviderConfigurationError(
            "?? ??? LLM provider? ?? health probe? ?????."
        )

    def _iter_provider_clients(self) -> list[tuple[str, Any]]:
        if self.llm_provider == "none":
            return []
        if self.llm_provider == "openai":
            return [("openai", self.openai)]
        if self.llm_provider == "gemini":
            return [("gemini", self.gemini)]
        return [("openai", self.openai), ("gemini", self.gemini)]
