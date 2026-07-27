"""
AUTOMA Schemas - VideoTemplate.

Pydantic models for video template request/response validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VideoTemplateCreate(BaseModel):
    """Schema for creating a video template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=100)
    pipeline_config: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured JSON list representing pipeline stages and node parameters",
    )


class VideoTemplateUpdate(BaseModel):
    """Schema for updating a video template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=100)
    pipeline_config: list[dict[str, Any]] | None = None
    is_active: bool | None = None


class VideoTemplateResponse(BaseModel):
    """Schema for video template responses."""

    id: str
    name: str
    description: str | None
    category: str | None
    pipeline_config: list[dict[str, Any]]
    versions_history: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class VideoTemplateListResponse(BaseModel):
    """Schema for listing video templates."""

    templates: list[VideoTemplateResponse]
    total: int
