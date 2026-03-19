from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from app.services.source_refs import collect_source_ref_ids


class PayloadSchemaValidationError(ValueError):
    """Raised when provider output does not match the declared JSON schema."""


class JsonSchemaValidator:
    def validate(self, *, page_key: str, schema: dict[str, Any], payload: dict[str, Any]) -> None:
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
        if not errors:
            self._validate_source_ref_links(payload)
            return

        first_error = errors[0]
        raise PayloadSchemaValidationError(
            f"{page_key} payload failed schema validation at "
            f"{self._format_path(first_error)}: {first_error.message}"
        )

    def _format_path(self, error: ValidationError) -> str:
        if not error.path:
            return "<root>"
        return ".".join(str(part) for part in error.path)

    def _validate_source_ref_links(self, payload: dict[str, Any]) -> None:
        source_refs = payload.get("sourceRefs", [])
        source_ref_ids = [ref.get("id", "") for ref in source_refs if isinstance(ref, dict)]
        known_ids = set(source_ref_ids)
        if len(known_ids) != len(source_ref_ids):
            raise PayloadSchemaValidationError("sourceRefs.id 는 중복되면 안 됩니다.")

        linked_ids = collect_source_ref_ids(payload)
        unknown_ids = sorted(linked_ids - known_ids)
        if unknown_ids:
            raise PayloadSchemaValidationError(
                f"sourceRefIds 가 sourceRefs 에 없는 id 를 참조합니다: {', '.join(unknown_ids)}"
            )
