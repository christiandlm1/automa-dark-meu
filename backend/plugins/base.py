"""
AUTOMA Plugins - Base Interfaces.

Abstract base classes and interfaces defining media processor plugins.
De-couples the Processing Engine from specific backends (FFmpeg, OpenCV, Whisper, etc.).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseMediaPlugin(ABC):
    """Abstract Base Class for all media processing plugins."""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Return the unique name of the plugin."""
        pass

    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Return the plugin version string."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if dependencies (CLI binaries, libraries) are met and available on system."""
        pass


class VideoProcessorPlugin(BaseMediaPlugin):
    """Interface for video manipulation tasks (cropping, zooming, filters)."""

    @abstractmethod
    async def apply_crop(self, input_path: Path, output_path: Path, x: int, y: int, width: int, height: int) -> Path:
        """Crop a video region and return output path."""
        pass

    @abstractmethod
    async def apply_zoom(self, input_path: Path, output_path: Path, factor: float) -> Path:
        """Apply zoom magnification scale to the video."""
        pass

    @abstractmethod
    async def apply_color_grading(
        self,
        input_path: Path,
        output_path: Path,
        contrast: float,
        brightness: float,
        saturation: float,
        bg_color: str | None = None,
        primary_color: str | None = None,
        secondary_color: str | None = None,
    ) -> Path:
        """Apply contrast, brightness, saturation adjustments and tint filters."""
        pass

    @abstractmethod
    async def apply_sharpness(self, input_path: Path, output_path: Path, intensity: float) -> Path:
        """Apply video sharpening filter."""
        pass

    @abstractmethod
    async def render_pipeline(self, input_path: Path, output_path: Path, nodes: list[dict[str, Any]]) -> Path:
        """Execute a chain of editing nodes sequentially on a video file."""
        pass


class AudioProcessorPlugin(BaseMediaPlugin):
    """Interface for audio manipulation tasks (levels, fades)."""

    @abstractmethod
    async def adjust_volume(self, input_path: Path, output_path: Path, volume_db: float) -> Path:
        """Adjust overall volume in decibels."""
        pass

    @abstractmethod
    async def apply_fades(self, input_path: Path, output_path: Path, fade_in_sec: float, fade_out_sec: float) -> Path:
        """Apply audio fade-in and fade-out envelopes."""
        pass


class TranscriberPlugin(BaseMediaPlugin):
    """Interface for speech-to-text transcription services."""

    @abstractmethod
    async def transcribe(self, input_path: Path) -> dict[str, Any]:
        """Transcribe spoken words from video or audio and return structured segment/subtitle data."""
        pass
