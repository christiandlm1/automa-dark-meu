"""
AUTOMA Repositories - Job Repository.

Database access layer for the ``jobs`` table.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from models.job import Job
from repositories.base_repository import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for Job CRUD operations."""

    model = Job

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_project(self, project_id: str) -> Sequence[Job]:
        """Return all jobs for a specific project with related video and template loaded."""
        stmt = (
            select(Job)
            .where(Job.project_id == project_id)
            .options(joinedload(Job.video), joinedload(Job.template), joinedload(Job.export_profile))
            .order_by(Job.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_job_with_relations(self, job_id: str) -> Job | None:
        """Find a job by ID and load relations."""
        stmt = (
            select(Job)
            .where(Job.id == job_id)
            .options(joinedload(Job.video), joinedload(Job.template), joinedload(Job.export_profile))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_jobs(self, limit: int = 50) -> Sequence[Job]:
        """Find all pending jobs in order of creation."""
        stmt = (
            select(Job)
            .where(Job.status == "pending")
            .options(joinedload(Job.video), joinedload(Job.template), joinedload(Job.export_profile))
            .order_by(Job.priority.desc(), Job.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_running_jobs(self) -> Sequence[Job]:
        """Find all currently executing jobs."""
        stmt = (
            select(Job)
            .where(Job.status == "running")
            .options(joinedload(Job.video), joinedload(Job.template), joinedload(Job.export_profile))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
