from fastapi import APIRouter, Query

from app.schemas.snapshots import (
    ResearchSnapshotCreate,
    SnapshotDeleteResponse,
    SnapshotListResponse,
    SnapshotMutationResponse,
)
from app.services.research_snapshot_store import ResearchSnapshotStore

router = APIRouter(prefix="/snapshots", tags=["snapshots"])
store = ResearchSnapshotStore()


@router.get("", response_model=SnapshotListResponse)
async def list_snapshots(
    symbol: str | None = Query(default=None, description="종목 티커")
) -> SnapshotListResponse:
    return SnapshotListResponse(snapshots=store.list(symbol=symbol))


@router.post("", response_model=SnapshotMutationResponse)
async def create_snapshot(
    payload: ResearchSnapshotCreate,
) -> SnapshotMutationResponse:
    return SnapshotMutationResponse(snapshot=store.create(payload))


@router.delete("/{snapshot_id}", response_model=SnapshotDeleteResponse)
async def delete_snapshot(snapshot_id: str) -> SnapshotDeleteResponse:
    return SnapshotDeleteResponse(
        deleted=store.delete(snapshot_id),
        id=snapshot_id,
    )
