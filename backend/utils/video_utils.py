"""
AUTOMA Utils - Video Utilities.

Extracts video metadata using pymediainfo and provides a typed dataclass.
CPU-bound — should be called from a thread pool executor.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
from pymediainfo import MediaInfo


@dataclass
class VideoMetadata:
    """Structured container for extracted video metadata."""

    duration: float | None = None       # seconds
    fps: float | None = None
    width: int | None = None
    height: int | None = None
    resolution: str | None = None       # e.g. "1920x1080"
    codec: str | None = None
    bitrate: int | None = None          # bits per second
    size_bytes: int = 0


def extract_video_metadata(file_path: str) -> VideoMetadata:
    """
    Extract technical metadata from a video file using pymediainfo.

    Falls back to OpenCV for fps / resolution when pymediainfo data is
    incomplete.  This is a CPU-bound operation.

    Args:
        file_path: Absolute path to the video file.

    Returns:
        Populated ``VideoMetadata`` instance.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    meta = VideoMetadata(size_bytes=path.stat().st_size)

    # --- pymediainfo ---
    media_info = MediaInfo.parse(str(path))

    for track in media_info.tracks:
        if track.track_type == "Video":
            meta.duration = (
                track.duration / 1000.0 if track.duration else None
            )
            meta.fps = (
                float(track.frame_rate) if track.frame_rate else None
            )
            meta.width = (
                int(track.width) if track.width else None
            )
            meta.height = (
                int(track.height) if track.height else None
            )
            meta.codec = track.codec_id or track.format
            meta.bitrate = (
                int(track.bit_rate) if track.bit_rate else None
            )
            break  # use the first video track

        if track.track_type == "General" and meta.duration is None:
            meta.duration = (
                track.duration / 1000.0 if track.duration else None
            )
            if meta.bitrate is None and track.overall_bit_rate:
                meta.bitrate = int(track.overall_bit_rate)

    # --- OpenCV fallback for width / height / fps ---
    if meta.width is None or meta.height is None or meta.fps is None:
        cap = cv2.VideoCapture(str(path))
        try:
            if cap.isOpened():
                if meta.width is None:
                    meta.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
                if meta.height is None:
                    meta.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None
                if meta.fps is None:
                    fps_val = cap.get(cv2.CAP_PROP_FPS)
                    meta.fps = float(fps_val) if fps_val > 0 else None
                if meta.duration is None:
                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    if frame_count > 0 and meta.fps and meta.fps > 0:
                        meta.duration = frame_count / meta.fps
        finally:
            cap.release()

    # Build resolution string
    if meta.width and meta.height:
        meta.resolution = f"{meta.width}x{meta.height}"

    return meta
