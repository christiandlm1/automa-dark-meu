"""
AUTOMA Schemas - History.

Pydantic models for history request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel


class HistoryResponse(BaseModel):
    """Schema for history records."""

    id: str
    project_id: str
    video_id: str | None
    video_name: str
    template_id: str | None
    template_name: str
    processed_at: datetime
    execution_time: float
    status: str
    log: str | None
    exported_path: str | None
    retry_count: int = 0
    attempts_details: str | None = None
    speed: float = 0.0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    gpu_usage: float = 0.0

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    """Schema for listing history records."""

    history: list[HistoryResponse]
    total: int
