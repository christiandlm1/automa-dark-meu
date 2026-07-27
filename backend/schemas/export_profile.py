"""
AUTOMA Schemas - Export Profile.

Pydantic models for export profile request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ExportProfileCreate(BaseModel):
    """Schema for creating a new export profile."""

    name: str = Field(..., description="Profile name")
    resolution: str | None = Field(None, description="Resolution (e.g. 1920x1080)")
    fps: float | None = Field(None, description="Frames per second")
    codec: str | None = Field(None, description="Video codec (e.g. h264)")
    bitrate: str | None = Field(None, description="Target bitrate (e.g. 5M)")
    is_custom: bool = Field(True, description="Whether this is a user-created profile")


class ExportProfileUpdate(BaseModel):
    """Schema for updating an export profile."""

    name: str | None = None
    resolution: str | None = None
    fps: float | None = None
    codec: str | None = None
    bitrate: str | None = None
    is_custom: bool | None = None


class ExportProfileResponse(BaseModel):
    """Schema for export profile responses."""

    id: str
    name: str
    resolution: str | None
    fps: float | None
    codec: str | None
    bitrate: str | None
    is_custom: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExportProfileListResponse(BaseModel):
    """Schema for listing export profiles."""

    profiles: list[ExportProfileResponse]
    total: int
