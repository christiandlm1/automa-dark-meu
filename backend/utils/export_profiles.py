"""
AUTOMA Utils - Export Profiles.

Provides predefined profile configurations for target platforms (Instagram, TikTok, YouTube, etc.).
Decouples export specifications from hardcoded templates.
"""

from typing import Any, Dict


class ExportProfile:
    """Predefined target profile presets for social network encoding constraints."""

    def __init__(
        self,
        name: str,
        resolution: str,
        fps: int,
        codec: str,
        bitrate: int,  # in kbps
        container: str,
    ) -> None:
        self.name = name
        self.resolution = resolution
        self.fps = fps
        self.codec = codec
        self.bitrate = bitrate
        self.container = container

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to serializable configuration dictionary."""
        return {
            "name": self.name,
            "resolution": self.resolution,
            "fps": self.fps,
            "codec": self.codec,
            "bitrate": self.bitrate,
            "format": self.container,
        }


# Preset social media formats
EXPORT_PROFILES = {
    "instagram": ExportProfile(
        name="Instagram Reels / Stories",
        resolution="1080x1920",
        fps=30,
        codec="h264",
        bitrate=4000,
        container="mp4",
    ),
    "tiktok": ExportProfile(
        name="TikTok Vertical HD",
        resolution="1080x1920",
        fps=60,
        codec="h264",
        bitrate=5000,
        container="mp4",
    ),
    "youtube_shorts": ExportProfile(
        name="YouTube Shorts High-Quality",
        resolution="1080x1920",
        fps=30,
        codec="h264",
        bitrate=6000,
        container="mp4",
    ),
    "facebook": ExportProfile(
        name="Facebook Desktop Landscape",
        resolution="1920x1080",
        fps=30,
        codec="h264",
        bitrate=4000,
        container="mp4",
    ),
    "pinterest": ExportProfile(
        name="Pinterest Square Pin",
        resolution="1080x1080",
        fps=24,
        codec="h264",
        bitrate=2500,
        container="mp4",
    ),
}
