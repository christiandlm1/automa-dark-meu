"""
AUTOMA Plugins - OpenCV Adaptor.

OpenCV implementation shell. In Módulo 02, this serves as a mock
that logs actions and copies files, preparing the ground for Módulo 03.
"""

import shutil
from pathlib import Path
from typing import Any

from plugins.base import VideoProcessorPlugin


class OpenCVPlugin(VideoProcessorPlugin):
    """OpenCV wrapper for image manipulations, scaling, filtering, and smart cropping."""

    @property
    def plugin_name(self) -> str:
        return "opencv"

    @property
    def plugin_version(self) -> str:
        return "1.0.0-mock"

    def is_available(self) -> bool:
        # In Módulo 02, return True.
        # In Módulo 03, we will verify imported cv2 is functional.
        return True

    async def apply_crop(self, input_path: Path, output_path: Path, x: int, y: int, width: int, height: int) -> Path:
        print(f"[OpenCVPlugin] Mock Crop: {input_path} -> {output_path} ({x},{y},{width},{height})")
        shutil.copy2(input_path, output_path)
        return output_path

    async def apply_zoom(self, input_path: Path, output_path: Path, factor: float) -> Path:
        print(f"[OpenCVPlugin] Mock Zoom: {input_path} -> {output_path} (x{factor})")
        shutil.copy2(input_path, output_path)
        return output_path

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
        print(f"[OpenCVPlugin] Mock Color: {input_path} -> {output_path}")
        shutil.copy2(input_path, output_path)
        return output_path

    async def apply_sharpness(self, input_path: Path, output_path: Path, intensity: float) -> Path:
        print(f"[OpenCVPlugin] Mock Sharpness: {input_path} -> {output_path}")
        shutil.copy2(input_path, output_path)
        return output_path

    async def render_pipeline(self, input_path: Path, output_path: Path, nodes: list[dict[str, Any]]) -> Path:
        print(f"[OpenCVPlugin] Rendering pipeline with {len(nodes)} nodes")
        shutil.copy2(input_path, output_path)
        return output_path
