"""
AUTOMA Routes - Projects
API route definitions for project operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.project_controller import ProjectController
from schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project and initialize its folders/database."""
    controller = ProjectController(db)
    return await controller.create(data)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all projects."""
    controller = ProjectController(db)
    return await controller.list_all(skip=skip, limit=limit)


@router.get("/recent", response_model=list[dict])
async def get_recent_projects(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get recently opened projects."""
    controller = ProjectController(db)
    return await controller.get_recent(limit=limit)


@router.get("/search", response_model=ProjectListResponse)
async def search_projects(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search projects by name."""
    controller = ProjectController(db)
    return await controller.search(query=q, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single project by ID."""
    controller = ProjectController(db)
    return await controller.get(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update project details."""
    controller = ProjectController(db)
    return await controller.update(project_id, data)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project (soft-delete)."""
    controller = ProjectController(db)
    return await controller.delete(project_id)


@router.post("/{project_id}/open", response_model=ProjectResponse)
async def open_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Open a project and track in recent projects list."""
    controller = ProjectController(db)
    return await controller.open(project_id)
