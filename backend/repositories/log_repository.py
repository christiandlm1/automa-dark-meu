"""
AUTOMA Repositories - Log Repository.

Database access layer for the ``logs`` table.
"""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log import Log
from repositories.base_repository import BaseRepository


class LogRepository(BaseRepository[Log]):
    """Repository for Log CRUD and queries."""

    model = Log

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Log]:
        """Return logs associated with a project, newest first."""
        stmt = (
            select(Log)
            .where(Log.project_id == project_id)
            .order_by(Log.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_level(
        self,
        level: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Log]:
        """Return logs filtered by severity level."""
        stmt = (
            select(Log)
            .where(Log.level == level)
            .order_by(Log.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Log]:
        """Return logs filtered by action type."""
        stmt = (
            select(Log)
            .where(Log.action == action)
            .order_by(Log.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent(self, limit: int = 50) -> Sequence[Log]:
        """Return the most recent log entries."""
        stmt = (
            select(Log)
            .order_by(Log.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_project(self, project_id: str) -> int:
        """Count log entries for a given project."""
        stmt = (
            select(func.count())
            .select_from(Log)
            .where(Log.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
