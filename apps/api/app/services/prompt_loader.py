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
    output_schema: dict


class PromptLoader:
    PAGE_DIR_MAP = {
        "overview": "overview",
        "radar": "radar",
        "stocks": "stock_detail",
        "history": "history",
    }

    def __init__(self, prompt_root: Path) -> None:
        self.prompt_root = prompt_root

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
            output_schema=self._read_json(page_root / "output.schema.json"),
        )

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8").strip()

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))
