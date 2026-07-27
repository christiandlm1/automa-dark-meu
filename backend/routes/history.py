"""
AUTOMA Routes - History.

API route definitions for execution history log querying.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.history_controller import HistoryController
from schemas.history import HistoryListResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/project/{project_id}", response_model=HistoryListResponse)
async def get_history_by_project(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Query paginated execution log history for a project."""
    controller = HistoryController(db)
    return await controller.list_by_project(project_id, skip=skip, limit=limit)


@router.delete("/project/{project_id}")
async def clear_history_by_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Clear all finished log history inside a project."""
    controller = HistoryController(db)
    return await controller.clear(project_id)


@router.get("/project/{project_id}/benchmarks")
async def get_project_benchmarks_endpoint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve computed execution speed, node and hardware benchmark averages for a project."""
    from processing.engine.metrics_engine import metrics_engine
    return await metrics_engine.get_project_benchmarks(db, project_id)
