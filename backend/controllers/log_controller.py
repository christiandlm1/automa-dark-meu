"""
AUTOMA Controllers - Log Controller.

Thin controller that delegates to LogService.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.log import LogCreate, LogListResponse, LogResponse
from services.log_service import LogService


class LogController:
    """Handles HTTP request/response translation for log endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.service = LogService(session)

    async def create(self, data: LogCreate) -> LogResponse:
        """Create a new log entry."""
        log = await self.service.create_log(data)
        return LogResponse.model_validate(log)

    async def get(self, log_id: str) -> LogResponse:
        """Get a single log entry."""
        log = await self.service.get_log(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Log not found: {log_id}",
            )
        return LogResponse.model_validate(log)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        project_id: str | None = None,
        level: str | None = None,
        action: str | None = None,
    ) -> LogListResponse:
        """List log entries with optional filters."""
        logs, total = await self.service.list_logs(
            skip=skip,
            limit=limit,
            project_id=project_id,
            level=level,
            action=action,
        )
        return LogListResponse(
            logs=[LogResponse.model_validate(l) for l in logs],
            total=total,
        )

    async def get_recent(self, limit: int = 50) -> list[LogResponse]:
        """Return the most recent log entries."""
        logs = await self.service.get_recent_logs(limit=limit)
        return [LogResponse.model_validate(l) for l in logs]
