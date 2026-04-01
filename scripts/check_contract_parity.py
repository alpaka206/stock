from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.schemas.common import Confidence, MissingDataItem, SourceRef, SourcedText  # noqa: E402
from app.schemas.history import HistoryResponse  # noqa: E402
from app.schemas.overview import OverviewResponse  # noqa: E402
from app.schemas.radar import RadarResponse  # noqa: E402
from app.schemas.stocks import StockDetailResponse  # noqa: E402


COMMON_SCHEMA_PATH = ROOT / "packages" / "contracts" / "schemas" / "common.schema.json"
PAGE_CONFIG = {
    "overview": {
        "contract": ROOT / "packages" / "contracts" / "schemas" / "overview.schema.json",
        "prompt_copy": ROOT / "apps" / "api" / "prompts" / "overview" / "output.schema.json",
        "model": OverviewResponse,
    },
    "radar": {
        "contract": ROOT / "packages" / "contracts" / "schemas" / "radar.schema.json",
        "prompt_copy": ROOT / "apps" / "api" / "prompts" / "radar" / "output.schema.json",
        "model": RadarResponse,
    },
    "stocks": {
        "contract": ROOT / "packages" / "contracts" / "schemas" / "stocks.schema.json",
        "prompt_copy": ROOT / "apps" / "api" / "prompts" / "stock_detail" / "output.schema.json",
        "model": StockDetailResponse,
    },
    "history": {
        "contract": ROOT / "packages" / "contracts" / "schemas" / "history.schema.json",
        "prompt_copy": ROOT / "apps" / "api" / "prompts" / "history" / "output.schema.json",
        "model": HistoryResponse,
    },
}

COMMON_SCHEMA_COMMENT = (
    "Canonical contract fragments for runtime payload validation. "
    "Page-level prompt output schema copies stay under apps/api/prompts/* for OpenAI structured output."
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def model_field_names(model: type) -> set[str]:
    return set(model.model_fields.keys())


def required_model_field_names(model: type) -> set[str]:
    return {
        field_name
        for field_name, field_info in model.model_fields.items()
        if field_info.is_required()
    }


def normalize_for_prompt_copy(schema: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(schema))
    normalized.pop("$comment", None)
    normalized.pop("$schema", None)
    normalized.pop("$id", None)
    normalized.pop("title", None)
    normalized.pop("required", None)
    return normalized


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_common_schema(errors: list[str]) -> None:
    common_schema = load_json(COMMON_SCHEMA_PATH)
    defs = common_schema.get("$defs", {})

    expect(
        common_schema.get("$comment") == COMMON_SCHEMA_COMMENT,
        "common.schema.json must document the canonical contract / prompt compatibility split.",
        errors,
    )
    expect(
        set(defs.get("sourceRef", {}).get("required", [])) == model_field_names(SourceRef),
        "common.sourceRef required fields drifted from Pydantic SourceRef.",
        errors,
    )
    expect(
        set(defs.get("missingDataItem", {}).get("required", []))
        == model_field_names(MissingDataItem),
        "common.missingDataItem required fields drifted from Pydantic MissingDataItem.",
        errors,
    )
    expect(
        set(defs.get("confidence", {}).get("required", [])) == model_field_names(Confidence),
        "common.confidence required fields drifted from Pydantic Confidence.",
        errors,
    )
    expect(
        defs.get("confidence", {}).get("properties", {}).get("score", {}).get("minimum") == 0,
        "common.confidence.score minimum must stay at 0.",
        errors,
    )
    expect(
        defs.get("confidence", {}).get("properties", {}).get("score", {}).get("maximum") == 1,
        "common.confidence.score maximum must stay at 1.",
        errors,
    )
    expect(
        set(defs.get("sourcedText", {}).get("required", [])) == model_field_names(SourcedText),
        "common.sourcedText required fields drifted from Pydantic SourcedText.",
        errors,
    )
    expect(
        set(defs.get("scoreBreakdownItem", {}).get("required", []))
        == {"label", "score", "summary"},
        "common.scoreBreakdownItem drifted from the shared score breakdown contract.",
        errors,
    )


def check_contract_against_model(
    *,
    page_key: str,
    contract_schema: dict[str, Any],
    model: type,
    errors: list[str],
) -> None:
    model_properties = model_field_names(model)
    model_required = required_model_field_names(model)
    contract_properties = set(contract_schema.get("properties", {}).keys())
    contract_required = set(contract_schema.get("required", []))

    expect(
        contract_properties == model_properties,
        f"{page_key}: canonical contract properties mismatch. schema={sorted(contract_properties)} model={sorted(model_properties)}",
        errors,
    )
    expect(
        contract_required == model_required,
        f"{page_key}: canonical contract required fields mismatch. schema={sorted(contract_required)} model={sorted(model_required)}",
        errors,
    )

    shared_fields = {"asOf", "sourceRefs", "missingData", "confidence"}
    for field_name in sorted(shared_fields):
        expect(
            field_name in contract_required,
            f"{page_key}: canonical contract must require shared field {field_name}.",
            errors,
        )

def check_prompt_copy_alignment(
    *,
    page_key: str,
    contract_schema: dict[str, Any],
    prompt_copy_schema: dict[str, Any],
    errors: list[str],
) -> None:
    expected_comment = (
        "Compatibility LLM structured-output schema copy. "
        f"Canonical API contract: packages/contracts/schemas/{page_key}.schema.json"
    )
    contract_required = set(contract_schema.get("required", []))
    prompt_required = set(prompt_copy_schema.get("required", []))

    expect(
        prompt_copy_schema.get("$comment") == expected_comment,
        f"{page_key}: prompt output schema copy must declare canonical source and compatibility status.",
        errors,
    )
    expect(
        prompt_required == contract_required,
        f"{page_key}: prompt copy required fields must exactly match canonical contract required fields.",
        errors,
    )
    expect(
        normalize_for_prompt_copy(prompt_copy_schema)
        == normalize_for_prompt_copy(contract_schema),
        f"{page_key}: prompt output schema copy drifted from canonical contract outside top-level required fields.",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    check_common_schema(errors)

    for page_key, config in PAGE_CONFIG.items():
        contract_schema = load_json(config["contract"])
        prompt_copy_schema = load_json(config["prompt_copy"])
        check_contract_against_model(
            page_key=page_key,
            contract_schema=contract_schema,
            model=config["model"],
            errors=errors,
        )
        check_prompt_copy_alignment(
            page_key=page_key,
            contract_schema=contract_schema,
            prompt_copy_schema=prompt_copy_schema,
            errors=errors,
        )

    if errors:
        print("Contract parity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Contract parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
