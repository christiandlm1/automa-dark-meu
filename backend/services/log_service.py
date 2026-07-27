"""
AUTOMA Services - Log Service.

Business logic for audit logging of user and system actions.
"""

import json
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.log import Log
from repositories.log_repository import LogRepository
from schemas.log import LogCreate


class LogService:
    """Records and queries audit log entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LogRepository(session)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def log(
        self,
        action: str,
        message: str,
        level: str = "info",
        project_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> Log:
        """
        Create a log entry (convenience method used across services).

        Args:
            action: Short action verb (e.g. "import", "delete").
            message: Human-readable message.
            level: Severity — "info", "warning", or "error".
            project_id: Optional linked project UUID.
            details: Optional dict serialised to JSON string.

        Returns:
            The created Log instance.
        """
        entry = Log(
            project_id=project_id,
            level=level,
            action=action,
            message=message,
            details=json.dumps(details, ensure_ascii=False) if details else None,
        )
        return await self.repo.create(entry)

    async def log_info(
        self, action: str, message: str, **kwargs: Any
    ) -> Log:
        """Shortcut for info-level logs."""
        return await self.log(action=action, message=message, level="info", **kwargs)

    async def log_warning(
        self, action: str, message: str, **kwargs: Any
    ) -> Log:
        """Shortcut for warning-level logs."""
        return await self.log(action=action, message=message, level="warning", **kwargs)

    async def log_error(
        self, action: str, message: str, **kwargs: Any
    ) -> Log:
        """Shortcut for error-level logs."""
        return await self.log(action=action, message=message, level="error", **kwargs)

    async def create_log(self, data: LogCreate) -> Log:
        """Create a log from a schema object."""
        return await self.log(
            action=data.action,
            message=data.message,
            level=data.level,
            project_id=data.project_id,
            details=json.loads(data.details) if data.details else None,
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_log(self, log_id: str) -> Log | None:
        """Get a single log by ID."""
        return await self.repo.get_by_id(log_id)

    async def list_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        project_id: str | None = None,
        level: str | None = None,
        action: str | None = None,
    ) -> tuple[Sequence[Log], int]:
        """
        List logs with optional filters.

        Returns:
            Tuple of (logs, total_count).
        """
        if project_id:
            logs = await self.repo.get_by_project(project_id, skip=skip, limit=limit)
            total = await self.repo.count_by_project(project_id)
        elif level:
            logs = await self.repo.get_by_level(level, skip=skip, limit=limit)
            total = len(logs)  # approximate for filtered queries
        elif action:
            logs = await self.repo.get_by_action(action, skip=skip, limit=limit)
            total = len(logs)
        else:
            logs = await self.repo.get_all(skip=skip, limit=limit)
            total = await self.repo.count()

        return logs, total

    async def get_recent_logs(self, limit: int = 50) -> Sequence[Log]:
        """Return the most recent log entries."""
        return await self.repo.get_recent(limit=limit)
