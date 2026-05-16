from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    insert,
    select,
)

from app.schemas.snapshots import ResearchSnapshot, ResearchSnapshotCreate

MAX_RESEARCH_SNAPSHOTS = 120
ROOT = Path(__file__).resolve().parents[4]
DEFAULT_STORE_PATH = ROOT / "data" / "runtime" / "research_snapshots.json"

metadata = MetaData()

research_snapshots = Table(
    "research_snapshots",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("symbol", String(32), nullable=False, index=True),
    Column("name", String(160), nullable=False),
    Column("exchange", String(40), nullable=False),
    Column("security_code", String(40), nullable=False),
    Column("sector", String(80), nullable=False),
    Column("note", Text, nullable=False),
    Column("stance", String(16), nullable=False),
    Column("conviction", String(16), nullable=False),
    Column("price", Float, nullable=False),
    Column("change_percent", Float, nullable=False),
    Column("score", Float, nullable=False),
    Column("thesis", Text, nullable=False),
    Column("selected_event_title", String(240), nullable=True),
    Column("selected_event_date", String(40), nullable=True),
    Column("active_rule_labels", JSON, nullable=False, default=list),
    Column("preset_name", String(160), nullable=False, default=""),
    Column("created_at", DateTime(timezone=True), nullable=False, index=True),
)


class ResearchSnapshotStore:
    def __init__(self, path: Path | None = None) -> None:
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            self._store: SnapshotStoreProtocol = DatabaseSnapshotStore(database_url)
        else:
            self._store = FileSnapshotStore(path=path)

    def list(self, symbol: str | None = None) -> list[ResearchSnapshot]:
        return self._store.list(symbol=symbol)

    def create(self, payload: ResearchSnapshotCreate) -> ResearchSnapshot:
        return self._store.create(payload)

    def delete(self, snapshot_id: str) -> bool:
        return self._store.delete(snapshot_id)


class SnapshotStoreProtocol:
    def list(self, symbol: str | None = None) -> list[ResearchSnapshot]:
        raise NotImplementedError

    def create(self, payload: ResearchSnapshotCreate) -> ResearchSnapshot:
        raise NotImplementedError

    def delete(self, snapshot_id: str) -> bool:
        raise NotImplementedError


class DatabaseSnapshotStore(SnapshotStoreProtocol):
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
        metadata.create_all(self.engine)

    def list(self, symbol: str | None = None) -> list[ResearchSnapshot]:
        statement = select(research_snapshots).order_by(
            research_snapshots.c.created_at.desc()
        )
        if symbol:
            statement = statement.where(
                research_snapshots.c.symbol == symbol.strip().upper()
            )

        with self.engine.begin() as connection:
            rows = connection.execute(statement).mappings().all()

        return [row_to_snapshot(dict(row)) for row in rows]

    def create(self, payload: ResearchSnapshotCreate) -> ResearchSnapshot:
        snapshot = build_snapshot(payload)

        with self.engine.begin() as connection:
            connection.execute(
                delete(research_snapshots).where(research_snapshots.c.id == snapshot.id)
            )
            connection.execute(insert(research_snapshots).values(snapshot_to_row(snapshot)))
            prune_old_snapshots(connection)

        return snapshot

    def delete(self, snapshot_id: str) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(
                delete(research_snapshots).where(research_snapshots.c.id == snapshot_id)
            )
        return result.rowcount > 0


class FileSnapshotStore(SnapshotStoreProtocol):
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
            snapshot = build_snapshot(payload)
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
        temp_path = self.path.with_name(
            f"{self.path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        )
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.path)


def build_snapshot(payload: ResearchSnapshotCreate) -> ResearchSnapshot:
    return ResearchSnapshot(
        **payload.model_dump(exclude={"id", "createdAt"}),
        id=payload.id or uuid.uuid4().hex,
        createdAt=payload.createdAt or datetime.now(timezone.utc).isoformat(),
    )


def snapshot_to_row(snapshot: ResearchSnapshot) -> dict[str, Any]:
    return {
        "id": snapshot.id,
        "symbol": snapshot.symbol,
        "name": snapshot.name,
        "exchange": snapshot.exchange,
        "security_code": snapshot.securityCode,
        "sector": snapshot.sector,
        "note": snapshot.note,
        "stance": snapshot.stance,
        "conviction": snapshot.conviction,
        "price": snapshot.price,
        "change_percent": snapshot.changePercent,
        "score": snapshot.score,
        "thesis": snapshot.thesis,
        "selected_event_title": snapshot.selectedEventTitle,
        "selected_event_date": snapshot.selectedEventDate,
        "active_rule_labels": snapshot.activeRuleLabels,
        "preset_name": snapshot.presetName,
        "created_at": parse_datetime(snapshot.createdAt),
    }


def row_to_snapshot(row: dict[str, Any]) -> ResearchSnapshot:
    created_at = row["created_at"]
    created_at_value = (
        created_at.isoformat()
        if isinstance(created_at, datetime)
        else str(created_at)
    )

    return ResearchSnapshot(
        id=row["id"],
        symbol=row["symbol"],
        name=row["name"],
        exchange=row["exchange"],
        securityCode=row["security_code"],
        sector=row["sector"],
        note=row["note"],
        stance=row["stance"],
        conviction=row["conviction"],
        price=row["price"],
        changePercent=row["change_percent"],
        score=row["score"],
        thesis=row["thesis"],
        selectedEventTitle=row.get("selected_event_title"),
        selectedEventDate=row.get("selected_event_date"),
        activeRuleLabels=row.get("active_rule_labels") or [],
        presetName=row.get("preset_name") or "",
        createdAt=created_at_value,
    )


def parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed


def prune_old_snapshots(connection: Any) -> None:
    old_ids = [
        row.id
        for row in connection.execute(
            select(research_snapshots.c.id)
            .order_by(research_snapshots.c.created_at.desc())
            .offset(MAX_RESEARCH_SNAPSHOTS)
        )
    ]

    if not old_ids:
        return

    connection.execute(delete(research_snapshots).where(research_snapshots.c.id.in_(old_ids)))


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url
