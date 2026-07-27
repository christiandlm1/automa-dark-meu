"""
AUTOMA Controllers - Project Controller.

Thin controller that delegates to ProjectService.
No business logic lives here.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from services.project_service import ProjectService
from services.log_service import LogService


class ProjectController:
    """Handles HTTP request/response translation for project endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.service = ProjectService(session)
        self.log_service = LogService(session)

    async def create(self, data: ProjectCreate) -> ProjectResponse:
        """Create a new project."""
        project = await self.service.create_project(data)
        await self.log_service.log_info(
            action="create",
            message=f"Project created: {project.name}",
            project_id=project.id,
        )
        return await self.service.to_response(project)

    async def get(self, project_id: str) -> ProjectResponse:
        """Get a single project by ID."""
        project = await self.service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}",
            )
        return await self.service.to_response(project)

    async def list_all(
        self, skip: int = 0, limit: int = 100
    ) -> ProjectListResponse:
        """List all active projects."""
        projects, total = await self.service.list_projects(skip=skip, limit=limit)
        responses = [await self.service.to_response(p) for p in projects]
        return ProjectListResponse(projects=responses, total=total)

    async def search(
        self, query: str, skip: int = 0, limit: int = 50
    ) -> ProjectListResponse:
        """Search projects by name."""
        projects = await self.service.search_projects(query, skip=skip, limit=limit)
        responses = [await self.service.to_response(p) for p in projects]
        return ProjectListResponse(projects=responses, total=len(responses))

    async def update(
        self, project_id: str, data: ProjectUpdate
    ) -> ProjectResponse:
        """Update a project."""
        project = await self.service.update_project(project_id, data)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}",
            )
        await self.log_service.log_info(
            action="update",
            message=f"Project updated: {project.name}",
            project_id=project.id,
        )
        return await self.service.to_response(project)

    async def delete(self, project_id: str) -> dict[str, str]:
        """Soft-delete a project."""
        success = await self.service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}",
            )
        await self.log_service.log_info(
            action="delete",
            message=f"Project deleted: {project_id}",
            project_id=project_id,
        )
        return {"detail": "Project deleted successfully"}

    async def open(self, project_id: str) -> ProjectResponse:
        """Mark a project as recently opened."""
        project = await self.service.open_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}",
            )
        return await self.service.to_response(project)

    async def get_recent(self, limit: int = 10) -> list[dict]:
        """Return recently opened projects."""
        recent = await self.service.get_recent_projects(limit=limit)
        return [
            {
                "id": r.id,
                "project_id": r.project_id,
                "name": r.name,
                "path": r.path,
                "last_opened_at": r.last_opened_at.isoformat(),
            }
            for r in recent
        ]
