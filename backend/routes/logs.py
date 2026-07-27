"""
AUTOMA Routes - Logs
API route definitions for log viewer.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.log_controller import LogController
from schemas.log import LogCreate, LogListResponse, LogResponse

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("", response_model=LogResponse)
async def create_log(
    data: LogCreate,
    db: AsyncSession = Depends(get_db),
):
    """Log an action programmatically from the frontend."""
    controller = LogController(db)
    return await controller.create(data)


@router.get("", response_model=LogListResponse)
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    project_id: str | None = Query(None),
    level: str | None = Query(None),
    action: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve filtered log entries."""
    controller = LogController(db)
    return await controller.list_all(
        skip=skip,
        limit=limit,
        project_id=project_id,
        level=level,
        action=action,
    )


@router.get("/recent", response_model=list[LogResponse])
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve most recent log entries."""
    controller = LogController(db)
    return await controller.get_recent(limit=limit)
