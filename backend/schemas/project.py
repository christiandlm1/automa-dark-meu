"""
AUTOMA Schemas - Project.

Pydantic models for project request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    path: str = Field(..., min_length=1, description="Root directory path for the project")
    category: str | None = Field(None, max_length=100, description="Project category")


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    path: str | None = None
    category: str | None = None
    status: str | None = Field(None, pattern=r"^(active|archived|deleted)$")


class ProjectResponse(BaseModel):
    """Schema for project responses."""

    id: str
    name: str
    description: str | None = None
    path: str
    category: str | None = None
    database_path: str
    created_at: datetime
    updated_at: datetime
    status: str
    video_count: int = 0

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Schema for paginated project list responses."""

    projects: list[ProjectResponse]
    total: int
