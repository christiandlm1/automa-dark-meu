"""
AUTOMA Schemas - Log.

Pydantic models for log request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """Schema for creating a log entry."""

    project_id: str | None = None
    level: str = Field("info", pattern=r"^(info|warning|error)$")
    action: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1)
    details: str | None = None


class LogResponse(BaseModel):
    """Schema for log entry responses."""

    id: str
    project_id: str | None = None
    level: str
    action: str
    message: str
    details: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LogListResponse(BaseModel):
    """Schema for paginated log list responses."""

    logs: list[LogResponse]
    total: int
