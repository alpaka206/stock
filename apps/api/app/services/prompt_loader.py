from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PromptBundle:
    page_key: str
    page_dir: str
    common_rules: str
    source_policy: str
    output_contract: str
    system_prompt: str
    contract_schema: dict
    output_schema: dict


class PromptLoader:
    PAGE_DIR_MAP = {
        "overview": "overview",
        "radar": "radar",
        "stocks": "stock_detail",
        "history": "history",
    }
    CONTRACT_SCHEMA_MAP = {
        "overview": "overview.schema.json",
        "radar": "radar.schema.json",
        "stocks": "stocks.schema.json",
        "history": "history.schema.json",
    }

    def __init__(self, prompt_root: Path) -> None:
        self.prompt_root = prompt_root
        self.contract_root = Path(__file__).resolve().parents[4] / "packages" / "contracts" / "schemas"

    def load_page(self, page_key: str) -> PromptBundle:
        page_dir = self.PAGE_DIR_MAP[page_key]
        common_root = self.prompt_root / "common"
        page_root = self.prompt_root / page_dir

        return PromptBundle(
            page_key=page_key,
            page_dir=page_dir,
            common_rules=self._read_text(common_root / "system.rules.md"),
            source_policy=self._read_text(common_root / "source-policy.md"),
            output_contract=self._read_text(common_root / "output.contract.md"),
            system_prompt=self._read_text(page_root / "system.md"),
            contract_schema=self._read_contract_schema(page_key=page_key),
            output_schema=self._read_output_schema(page_root=page_root),
        )

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8").strip()

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_contract_schema(self, *, page_key: str) -> dict:
        contract_path = self.contract_root / self.CONTRACT_SCHEMA_MAP[page_key]
        return self._read_json(contract_path)

    def _read_output_schema(self, *, page_root: Path) -> dict:
        return self._read_json(page_root / "output.schema.json")
