"""
AUTOMA Repositories - Video Repository.

Database access layer for the ``videos`` table.
"""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.video import Video
from repositories.base_repository import BaseRepository


class VideoRepository(BaseRepository[Video]):
    """Repository for Video CRUD and queries."""

    model = Video

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Video]:
        """Return all videos belonging to a project, newest first."""
        stmt = (
            select(Video)
            .where(Video.project_id == project_id)
            .order_by(Video.imported_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_project(self, project_id: str) -> int:
        """Count videos in a project."""
        stmt = (
            select(func.count())
            .select_from(Video)
            .where(Video.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_hash(self, file_hash: str) -> Video | None:
        """Find a video by its xxhash digest (duplicate detection)."""
        stmt = select(Video).where(Video.hash == file_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_original_path(self, original_path: str) -> Video | None:
        """Find a video by its original file path."""
        stmt = select(Video).where(Video.original_path == original_path)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_status(
        self, status: str, project_id: str | None = None
    ) -> Sequence[Video]:
        """Get videos filtered by status, optionally within a project."""
        stmt = select(Video).where(Video.status == status)
        if project_id:
            stmt = stmt.where(Video.project_id == project_id)
        stmt = stmt.order_by(Video.imported_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_videos(
        self, project_id: str | None = None
    ) -> Sequence[Video]:
        """Convenience wrapper for videos awaiting scanning."""
        return await self.get_by_status("pending", project_id)
