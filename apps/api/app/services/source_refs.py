from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1
import re
from typing import Any


def build_source_ref(
    *,
    title: str,
    kind: str,
    publisher: str,
    published_at: str | datetime,
    source_key: str,
    url: str = "",
    symbol: str = "",
) -> dict[str, Any]:
    timestamp = _as_iso(published_at)
    identity = f"{kind}|{publisher}|{title}|{timestamp}|{url}|{source_key}|{symbol}"
    return {
        "id": sha1(identity.encode("utf-8")).hexdigest()[:12],
        "title": title,
        "kind": kind,
        "publisher": publisher,
        "publishedAt": timestamp,
        "url": url,
        "sourceKey": source_key,
        "symbol": symbol,
    }


def build_missing_data(field: str, reason: str, expected_source: str) -> dict[str, str]:
    return {
        "field": field,
        "reason": reason,
        "expectedSource": expected_source,
    }


def dedupe_source_refs(source_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for ref in source_refs:
        deduped[ref["id"]] = ref
    return list(deduped.values())


def collect_source_ref_ids(payload: Any) -> set[str]:
    collected: set[str] = set()
    _walk(payload, collected)
    return collected


def _walk(payload: Any, collected: set[str]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "sourceRefIds" and isinstance(value, list):
                collected.update(str(item) for item in value)
            else:
                _walk(value, collected)
    elif isinstance(payload, list):
        for item in payload:
            _walk(item, collected)


def _as_iso(value: str | datetime) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc).isoformat()
        return value.isoformat()
    if value:
        normalized = str(value).strip()
        if re.fullmatch(r"\d{8}", normalized):
            normalized = f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:8]}"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
            return f"{normalized}T00:00:00+00:00"
        try:
            return datetime.fromisoformat(normalized.replace("Z", "+00:00")).isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()
