from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptBundle


class OpenAIResearchClient:
    def __init__(self, *, api_key: str | None, model: str) -> None:
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_page_response(
        self,
        *,
        prompt_bundle: PromptBundle,
        page_key: str,
        facts: dict[str, Any],
        source_refs: list[dict[str, Any]],
        missing_data: list[dict[str, str]],
    ) -> dict[str, Any]:
        if self._client is None:
            raise ProviderConfigurationError(
                "real provider를 사용하려면 OPENAI_API_KEY가 필요합니다."
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

        response = await self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=json.dumps(user_payload, ensure_ascii=False),
            text={
                "format": {
                    "type": "json_schema",
                    "name": f"{page_key}_response",
                    "schema": prompt_bundle.output_schema,
                    "strict": True,
                }
            },
        )

        output_text = getattr(response, "output_text", "")
        if not output_text:
            output_text = self._extract_output_text(response)
        if not output_text:
            raise ExternalServiceError("OpenAI 응답에서 구조화된 JSON을 추출하지 못했습니다.")

        return json.loads(output_text)

    def _extract_output_text(self, response: Any) -> str:
        chunks: list[str] = []
        for item in getattr(response, "output", []):
            for content in getattr(item, "content", []):
                text = getattr(content, "text", None)
                if text:
                    chunks.append(text)
        return "".join(chunks)
