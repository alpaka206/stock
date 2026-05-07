from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.snapshots import ResearchSnapshot, ResearchSnapshotCreate

MAX_RESEARCH_SNAPSHOTS = 120
ROOT = Path(__file__).resolve().parents[4]
DEFAULT_STORE_PATH = ROOT / ".omx" / "runtime" / "research_snapshots.json"


class ResearchSnapshotStore:
    def __init__(self, path: Path | None = None) -> None:
        configured_path = os.environ.get("RESEARCH_SNAPSHOT_STORE_PATH")
        if path is not None:
            self.path = path
        elif configured_path:
            self.path = Path(configured_path)
        else:
            self.path = DEFAULT_STORE_PATH
        self._lock = threading.Lock()

    def list(self, symbol: str | None = None) -> list[ResearchSnapshot]:
        snapshots = self._read()
        if symbol:
            normalized_symbol = symbol.upper()
            snapshots = [
                snapshot
                for snapshot in snapshots
                if snapshot.symbol.upper() == normalized_symbol
            ]

        return sorted(snapshots, key=lambda snapshot: snapshot.createdAt, reverse=True)

    def create(self, payload: ResearchSnapshotCreate) -> ResearchSnapshot:
        with self._lock:
            snapshots = self._read_unlocked()
            snapshot = ResearchSnapshot(
                **payload.model_dump(exclude={"id", "createdAt"}),
                id=payload.id or uuid.uuid4().hex,
                createdAt=payload.createdAt or datetime.now(timezone.utc).isoformat(),
            )
            next_snapshots = [
                snapshot,
                *[item for item in snapshots if item.id != snapshot.id],
            ][:MAX_RESEARCH_SNAPSHOTS]
            self._write_unlocked(next_snapshots)
            return snapshot

    def delete(self, snapshot_id: str) -> bool:
        with self._lock:
            snapshots = self._read_unlocked()
            next_snapshots = [
                snapshot for snapshot in snapshots if snapshot.id != snapshot_id
            ]
            deleted = len(next_snapshots) != len(snapshots)
            if deleted:
                self._write_unlocked(next_snapshots)
            return deleted

    def _read(self) -> list[ResearchSnapshot]:
        with self._lock:
            return self._read_unlocked()

    def _read_unlocked(self) -> list[ResearchSnapshot]:
        if not self.path.exists():
            return []

        try:
            raw_payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        raw_snapshots = raw_payload.get("snapshots", [])
        if not isinstance(raw_snapshots, list):
            return []

        snapshots: list[ResearchSnapshot] = []
        for raw_snapshot in raw_snapshots:
            if not isinstance(raw_snapshot, dict):
                continue
            try:
                snapshots.append(ResearchSnapshot.model_validate(raw_snapshot))
            except ValueError:
                continue

        return snapshots

    def _write_unlocked(self, snapshots: list[ResearchSnapshot]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "snapshots": [
                snapshot.model_dump(mode="json") for snapshot in snapshots
            ]
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
