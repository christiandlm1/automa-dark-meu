"""
AUTOMA Repositories - Project Repository.

Database access layer for the ``projects`` table.
"""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.project import Project
from models.video import Video
from repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project CRUD and queries."""

    model = Project

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id_with_videos(self, project_id: str) -> Project | None:
        """Load a project together with its video collection."""
        stmt = (
            select(Project)
            .options(selectinload(Project.videos))
            .where(Project.id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Project | None:
        """Find a project by exact name."""
        stmt = select(Project).where(Project.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_path(self, path: str) -> Project | None:
        """Find a project by its root directory path."""
        stmt = select(Project).where(Project.path == path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_projects(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Project]:
        """Return only projects with status == 'active'."""
        stmt = (
            select(Project)
            .where(Project.status == "active")
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_active(self) -> int:
        """Count projects with status == 'active'."""
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.status == "active")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_video_count(self, project_id: str) -> int:
        """Return the number of videos belonging to a project."""
        stmt = (
            select(func.count())
            .select_from(Video)
            .where(Video.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search_by_name(
        self, query: str, skip: int = 0, limit: int = 50
    ) -> Sequence[Project]:
        """Case-insensitive search by project name."""
        stmt = (
            select(Project)
            .where(Project.name.ilike(f"%{query}%"))
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
