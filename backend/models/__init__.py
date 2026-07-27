"""
AUTOMA Models Package.

Re-exports every ORM model so that ``Base.metadata`` sees all tables
when ``init_database()`` is called.
"""

from models.project import Project
from models.video import Video
from models.settings import Setting
from models.log import Log
from models.hardware import Hardware
from models.recent_project import RecentProject
from models.video_template import VideoTemplate
from models.job import Job
from models.history import History
from models.export_profile import ExportProfile
from models.subtitle_preset import SubtitlePreset
from models.asset import Asset

__all__ = [
    "Project",
    "Video",
    "Setting",
    "Log",
    "Hardware",
    "RecentProject",
    "VideoTemplate",
    "Job",
    "History",
    "ExportProfile",
    "SubtitlePreset",
    "Asset",
]
