"""
AUTOMA Utils Package.

Shared utility functions for file, video, and system operations.
"""

from utils.file_utils import (
    compute_file_hash,
    get_file_extension,
    is_valid_video_extension,
    get_file_size,
    safe_copy_file,
    safe_move_file,
    safe_delete_file,
    ensure_directory,
)
from utils.video_utils import (
    extract_video_metadata,
    VideoMetadata,
)
from utils.system_utils import (
    get_system_info,
    get_realtime_usage,
)

__all__ = [
    "compute_file_hash",
    "get_file_extension",
    "is_valid_video_extension",
    "get_file_size",
    "safe_copy_file",
    "safe_move_file",
    "safe_delete_file",
    "ensure_directory",
    "extract_video_metadata",
    "VideoMetadata",
    "get_system_info",
    "get_realtime_usage",
]
