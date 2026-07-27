"""
AUTOMA Schemas Package.

Re-exports all Pydantic request/response schemas.
"""

from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from schemas.video import (
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoListResponse,
    VideoImportRequest,
)
from schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingListResponse,
)
from schemas.log import LogCreate, LogResponse, LogListResponse
from schemas.hardware import (
    HardwareResponse,
    HardwareMonitorResponse,
)
from schemas.video_template import (
    VideoTemplateCreate,
    VideoTemplateUpdate,
    VideoTemplateResponse,
    VideoTemplateListResponse,
)
from schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
)
from schemas.history import (
    HistoryResponse,
    HistoryListResponse,
)
from schemas.export_profile import (
    ExportProfileCreate,
    ExportProfileUpdate,
    ExportProfileResponse,
    ExportProfileListResponse,
)

__all__ = [
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "VideoCreate",
    "VideoUpdate",
    "VideoResponse",
    "VideoListResponse",
    "VideoImportRequest",
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    "SettingListResponse",
    "LogCreate",
    "LogResponse",
    "LogListResponse",
    "HardwareResponse",
    "HardwareMonitorResponse",
    "VideoTemplateCreate",
    "VideoTemplateUpdate",
    "VideoTemplateResponse",
    "VideoTemplateListResponse",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "HistoryResponse",
    "HistoryListResponse",
    "ExportProfileCreate",
    "ExportProfileUpdate",
    "ExportProfileResponse",
    "ExportProfileListResponse",
]
