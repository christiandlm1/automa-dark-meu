"""
AUTOMA Schemas - Job.

Pydantic models for job request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field

from schemas.video import VideoResponse
from schemas.video_template import VideoTemplateResponse
from schemas.export_profile import ExportProfileResponse


class JobCreate(BaseModel):
    """Schema for adding a video processing task to the queue."""

    project_id: str | None = Field(None, description="Parent project UUID")
    video_id: str = Field(..., description="Target video UUID to process")
    template_id: str | None = Field(None, description="Template UUID to apply")
    export_profile_id: str | None = Field(None, description="Export profile UUID to apply")


class JobUpdate(BaseModel):
    """Schema for updating job progress and status."""

    status: str | None = Field(None, pattern=r"^(pending|running|completed|failed|cancelled|paused)$")
    progress: float | None = Field(None, ge=0.0, le=100.0)
    speed: float | None = Field(None, ge=0.0)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    estimated_time: float | None = None
    error_message: str | None = None
    priority: int | None = None
    retry_count: int | None = None


class JobResponse(BaseModel):
    """Schema for job responses."""

    id: str
    project_id: str
    video_id: str
    template_id: str | None
    export_profile_id: str | None
    status: str
    progress: float
    speed: float
    started_at: datetime | None
    finished_at: datetime | None
    estimated_time: float | None
    error_message: str | None
    priority: int
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    # Nested properties
    video: VideoResponse | None = None
    template: VideoTemplateResponse | None = None
    export_profile: ExportProfileResponse | None = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Schema for listing jobs."""

    jobs: list[JobResponse]
    total: int


class JobPreviewRequest(BaseModel):
    """Schema for requesting a time-sliced rendering preview of a video and template."""

    video_id: str
    template_id: str
    start_time: float = Field(0.0, description="Start point in seconds")
    end_time: float = Field(3.0, description="End point in seconds")
