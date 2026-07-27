"""
AUTOMA Repositories - RecentProject Repository.

Database access layer for the ``recent_projects`` table.
"""

from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.recent_project import RecentProject
from repositories.base_repository import BaseRepository


class RecentProjectRepository(BaseRepository[RecentProject]):
    """Repository for RecentProject CRUD and queries."""

    model = RecentProject

    MAX_RECENT: int = 20  # keep only the N most recent entries

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_recent(self, limit: int = 10) -> Sequence[RecentProject]:
        """Return the most recently opened projects that are not deleted."""
        from models.project import Project
        stmt = (
            select(RecentProject)
            .join(Project, RecentProject.project_id == Project.id)
            .where(Project.status != "deleted")
            .order_by(RecentProject.last_opened_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_project_id(self, project_id: str) -> RecentProject | None:
        """Find a recent-project entry by its linked project_id."""
        stmt = select(RecentProject).where(
            RecentProject.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self, project_id: str, name: str, path: str
    ) -> RecentProject:
        """
        Insert or refresh a recent-project entry, then prune old entries.
        """
        from datetime import datetime, timezone

        existing = await self.get_by_project_id(project_id)
        if existing:
            existing.last_opened_at = datetime.now(timezone.utc)
            existing.name = name
            existing.path = path
            await self.session.flush()
            await self.session.refresh(existing)
            entry = existing
        else:
            entry = RecentProject(
                project_id=project_id, name=name, path=path
            )
            self.session.add(entry)
            await self.session.flush()
            await self.session.refresh(entry)

        # Prune to keep only MAX_RECENT entries
        await self._prune()
        return entry

    async def _prune(self) -> None:
        """Remove old entries beyond MAX_RECENT."""
        # Get IDs to keep
        keep_stmt = (
            select(RecentProject.id)
            .order_by(RecentProject.last_opened_at.desc())
            .limit(self.MAX_RECENT)
        )
        keep_result = await self.session.execute(keep_stmt)
        keep_ids = {row[0] for row in keep_result.fetchall()}

        if not keep_ids:
            return

        # Delete everything not in the keep set
        del_stmt = delete(RecentProject).where(
            RecentProject.id.notin_(keep_ids)
        )
        await self.session.execute(del_stmt)
        await self.session.flush()

    async def clear_all(self) -> None:
        """Remove all recent project entries."""
        stmt = delete(RecentProject)
        await self.session.execute(stmt)
        await self.session.flush()
