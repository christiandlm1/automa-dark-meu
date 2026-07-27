"""
AUTOMA Services - Project Service.

Business logic for project lifecycle management.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.project import Project
from repositories.project_repository import ProjectRepository
from repositories.recent_project_repository import RecentProjectRepository
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    """Encapsulates all business rules related to projects."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProjectRepository(session)
        self.recent_repo = RecentProjectRepository(session)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project, set up its directory structure,
        and register it in recent projects.
        """
        # Create project directory structure
        project_path = Path(data.path)
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "videos").mkdir(exist_ok=True)
        (project_path / "thumbnails").mkdir(exist_ok=True)

        # Database path inside the project directory
        db_path = str(project_path / "project.db")

        project = Project(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            path=str(project_path),
            category=data.category,
            database_path=db_path,
        )

        created = await self.repo.create(project)

        # Track as recently opened
        await self.recent_repo.upsert(
            project_id=created.id,
            name=created.name,
            path=created.path,
        )

        return created

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_project(self, project_id: str) -> Project | None:
        """Retrieve a project by ID."""
        return await self.repo.get_by_id(project_id)

    async def get_project_with_videos(self, project_id: str) -> Project | None:
        """Retrieve a project with its videos eagerly loaded."""
        return await self.repo.get_by_id_with_videos(project_id)

    async def list_projects(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Project], int]:
        """Return active projects and total count."""
        projects = await self.repo.get_active_projects(skip=skip, limit=limit)
        total = await self.repo.count_active()
        return projects, total

    async def search_projects(
        self, query: str, skip: int = 0, limit: int = 50
    ) -> Sequence[Project]:
        """Search projects by name."""
        return await self.repo.search_by_name(query, skip=skip, limit=limit)

    async def get_video_count(self, project_id: str) -> int:
        """Return the number of videos in a project."""
        return await self.repo.get_video_count(project_id)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update_project(
        self, project_id: str, data: ProjectUpdate
    ) -> Project | None:
        """Update project fields and refresh its recent-project entry."""
        project = await self.repo.get_by_id(project_id)
        if not project:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)
        updated = await self.repo.update(project, update_data)

        # Refresh recent-project entry
        await self.recent_repo.upsert(
            project_id=updated.id,
            name=updated.name,
            path=updated.path,
        )

        return updated

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and remove it from recent projects."""
        project = await self.repo.get_by_id(project_id)
        if not project:
            return False

        # Remove from recent_projects
        recent = await self.recent_repo.get_by_project_id(project_id)
        if recent:
            await self.recent_repo.delete(recent)

        # Delete project record
        await self.repo.delete_by_id(project_id)
        await self.session.commit()
        return True

    async def hard_delete_project(self, project_id: str) -> bool:
        """Permanently remove a project from the database."""
        return await self.repo.delete_by_id(project_id)

    # ------------------------------------------------------------------
    # Recent projects
    # ------------------------------------------------------------------

    async def get_recent_projects(self, limit: int = 10) -> Sequence:
        """Return the most recently opened projects."""
        return await self.recent_repo.get_recent(limit=limit)

    async def open_project(self, project_id: str) -> Project | None:
        """Mark a project as recently opened."""
        project = await self.repo.get_by_id(project_id)
        if not project:
            return None
        await self.recent_repo.upsert(
            project_id=project.id,
            name=project.name,
            path=project.path,
        )
        return project

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def to_response(self, project: Project) -> ProjectResponse:
        """Convert a Project ORM instance to a response schema."""
        video_count = await self.get_video_count(project.id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            path=project.path,
            category=project.category,
            database_path=project.database_path,
            created_at=project.created_at,
            updated_at=project.updated_at,
            status=project.status,
            video_count=video_count,
        )
