"""
AUTOMA Repositories - VideoTemplate Repository.

Database access layer for the ``video_templates`` table.
"""

from typing import Sequence

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.video_template import VideoTemplate
from repositories.base_repository import BaseRepository


class VideoTemplateRepository(BaseRepository[VideoTemplate]):
    """Repository for VideoTemplate CRUD operations."""

    model = VideoTemplate

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_active(self) -> Sequence[VideoTemplate]:
        """Get all active templates."""
        stmt = select(VideoTemplate).where(VideoTemplate.is_active == True).order_by(VideoTemplate.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(
        self,
        query: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[VideoTemplate]:
        """Search templates by name, description, or category."""
        stmt = select(VideoTemplate)
        filters = []
        
        if query:
            filters.append(
                or_(
                    VideoTemplate.name.icontains(query),
                    VideoTemplate.description.icontains(query),
                )
            )
        
        if category:
            filters.append(VideoTemplate.category == category)
            
        if filters:
            stmt = stmt.where(*filters)
            
        stmt = stmt.order_by(VideoTemplate.name).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
