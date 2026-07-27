"""
AUTOMA Services - Thumbnail Service.

Generates video thumbnails using opencv-python-headless.
All methods are CPU-bound and designed to be called from an executor.
"""

from pathlib import Path

import cv2

from config import settings


class ThumbnailService:
    """Generates and manages video thumbnail images."""

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        quality: int | None = None,
    ) -> None:
        self.width = width or getattr(settings, 'THUMBNAIL_WIDTH', 320)
        self.height = height or getattr(settings, 'THUMBNAIL_HEIGHT', 180)
        self.quality = quality or getattr(settings, 'THUMBNAIL_QUALITY', 85)

    def generate_thumbnail(
        self,
        video_path: str,
        video_id: str,
        timestamp_ratio: float = 0.1,
    ) -> str | None:
        """
        Extract a single frame from a video and save it as a JPEG thumbnail.

        The thumbnail is stored alongside the video in a ``thumbnails``
        directory relative to the video file's parent project directory.

        Args:
            video_path: Absolute path to the video file.
            video_id: UUID used as the thumbnail filename.
            timestamp_ratio: Position in the video to capture (0.0 – 1.0).
                             Defaults to 10 % through the video.

        Returns:
            Absolute path to the generated thumbnail, or None on failure.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                return None

            target_frame = int(total_frames * timestamp_ratio)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

            success, frame = cap.read()
            if not success or frame is None:
                # Fallback: try the very first frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = cap.read()
                if not success or frame is None:
                    return None

            # Resize to target dimensions
            resized = cv2.resize(
                frame,
                (self.width, self.height),
                interpolation=cv2.INTER_AREA,
            )

            # Determine output directory
            video_dir = Path(video_path).parent
            # Navigate up to the project root (parent of "videos" dir)
            if video_dir.name == "videos":
                thumb_dir = video_dir.parent / "thumbnails"
            else:
                thumb_dir = video_dir / "thumbnails"
            thumb_dir.mkdir(parents=True, exist_ok=True)

            thumb_path = thumb_dir / f"{video_id}.{settings.THUMBNAIL_FORMAT}"

            # Save with quality param
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.quality]
            cv2.imwrite(str(thumb_path), resized, encode_params)

            return str(thumb_path) if thumb_path.is_file() else None

        finally:
            cap.release()

    def delete_thumbnail(self, thumbnail_path: str) -> bool:
        """Delete a thumbnail file from disk."""
        path = Path(thumbnail_path)
        if path.is_file():
            path.unlink()
            return True
        return False
