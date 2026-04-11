from __future__ import annotations

import json
from typing import Any

import httpx

from app.services.errors import (
    ExternalRateLimitError,
    ExternalServiceError,
    ProviderConfigurationError,
)
from app.services.prompt_loader import PromptBundle


class GeminiResearchClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate_page_response(
        self,
        *,
        prompt_bundle: PromptBundle,
        page_key: str,
        facts: dict[str, Any],
        source_refs: list[dict[str, Any]],
        missing_data: list[dict[str, str]],
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderConfigurationError(
                "GEMINI_API_KEY is required for gemini provider mode."
            )

        instructions = "\n\n".join(
            [
                prompt_bundle.common_rules,
                prompt_bundle.source_policy,
                prompt_bundle.output_contract,
                prompt_bundle.system_prompt,
            ]
        )
        user_payload = {
            "pageKey": page_key,
            "facts": facts,
            "sourceRefs": source_refs,
            "missingData": missing_data,
            "rules": {
                "language": "ko-KR",
                "mustUseOnlyProvidedFacts": True,
                "mustReferenceSourceRefIds": True,
            },
        }
        request_payload = {
            "systemInstruction": {
                "parts": [{"text": instructions}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": json.dumps(user_payload, ensure_ascii=False)}
                    ],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": prompt_bundle.output_schema,
                "temperature": 0.2,
            },
        }

        payload = await self._request_json(request_payload, request_target=page_key)
        output_text = self._extract_output_text(payload)
        if not output_text:
            raise ExternalServiceError("Gemini did not return structured JSON output.")

        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ExternalServiceError("Gemini JSON output could not be parsed.") from exc

    async def probe_health(self) -> dict[str, bool]:
        if not self.api_key:
            raise ProviderConfigurationError(
                "GEMINI_API_KEY is required for gemini provider mode."
            )

        payload = await self._request_json(
            {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "health probe"}],
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseJsonSchema": {
                        "type": "object",
                        "properties": {"ok": {"type": "boolean"}},
                        "required": ["ok"],
                    },
                },
            },
            request_target="health probe",
        )
        output_text = self._extract_output_text(payload)
        if not output_text:
            raise ExternalServiceError("Gemini health probe returned empty output.")

        result = json.loads(output_text)
        if result.get("ok") is not True:
            raise ExternalServiceError("Gemini health probe returned an invalid payload.")
        return {"ok": True}

    async def _request_json(
        self, request_payload: dict[str, Any], *, request_target: str
    ) -> dict[str, Any]:
        endpoint = f"{self.base_url}/{self.model}:generateContent"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key or "",
                    },
                    json=request_payload,
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 429:
                raise ExternalRateLimitError(
                    f"Gemini {request_target} hit a rate limit."
                ) from exc
            raise ExternalServiceError(
                f"Gemini {request_target} failed with HTTP {status_code}."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                f"Gemini {request_target} timed out."
            ) from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError(
                f"Gemini {request_target} failed with a network error."
            ) from exc
        except ValueError as exc:
            raise ExternalServiceError(
                f"Gemini {request_target} returned invalid JSON."
            ) from exc

        if payload.get("promptFeedback", {}).get("blockReason"):
            block_reason = payload["promptFeedback"]["blockReason"]
            raise ExternalServiceError(
                f"Gemini {request_target} was blocked: {block_reason}"
            )
        return payload

    def _extract_output_text(self, payload: dict[str, Any]) -> str:
        for candidate in payload.get("candidates", []):
            content = candidate.get("content", {})
            parts = content.get("parts", []) if isinstance(content, dict) else []
            chunks = [
                part.get("text", "")
                for part in parts
                if isinstance(part, dict) and part.get("text")
            ]
            if chunks:
                return "".join(chunks)
        return ""
