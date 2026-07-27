"""
AUTOMA Repositories - History Repository.

Database access layer for the ``history`` table.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from repositories.base_repository import BaseRepository


class HistoryRepository(BaseRepository[History]):
    """Repository for History CRUD operations."""

    model = History

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[History]:
        """Return history records for a project ordered by completion timestamp."""
        stmt = (
            select(History)
            .where(History.project_id == project_id)
            .order_by(History.processed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_project(self, project_id: str) -> int:
        """Count total history entries for a specific project."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(History).where(History.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()
