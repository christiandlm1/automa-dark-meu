"""
AUTOMA Schemas - Video.

Pydantic models for video request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class VideoCreate(BaseModel):
    """Schema for creating a video record directly."""

    project_id: str = Field(..., description="Parent project UUID")
    name: str = Field(..., min_length=1, max_length=255)
    original_path: str = Field(..., min_length=1)
    project_path: str = Field(..., min_length=1)
    size_bytes: int = Field(..., ge=0)


class VideoImportRequest(BaseModel):
    """Schema for importing one or more video files into a project."""

    project_id: str = Field(..., description="Target project UUID")
    file_paths: list[str] = Field(
        ..., min_length=1, description="List of video file paths to import"
    )
    copy_to_project: bool = Field(
        True, description="Whether to copy files into the project directory"
    )


class VideoUpdate(BaseModel):
    """Schema for updating video metadata (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    notes: str | None = None
    status: str | None = Field(None, pattern=r"^(pending|scanned|error)$")
    thumbnail_path: str | None = None


class VideoResponse(BaseModel):
    """Schema for video responses."""

    id: str
    project_id: str
    name: str
    original_path: str
    project_path: str
    thumbnail_path: str | None = None
    duration: float | None = None
    fps: float | None = None
    width: int | None = None
    height: int | None = None
    resolution: str | None = None
    codec: str | None = None
    bitrate: int | None = None
    size_bytes: int
    hash: str | None = None
    status: str
    notes: str | None = None
    imported_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    """Schema for paginated video list responses."""

    videos: list[VideoResponse]
    total: int
