"""
AUTOMA Services - Scanner Service.

Scans pending videos to extract metadata (via pymediainfo / OpenCV)
and generate thumbnails.  Heavy work is offloaded to a thread pool.
"""

import asyncio
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.video import Video
from repositories.video_repository import VideoRepository
from services.thumbnail_service import ThumbnailService
from utils.video_utils import extract_video_metadata


class ScannerService:
    """Orchestrates metadata extraction and thumbnail generation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VideoRepository(session)
        self.thumbnail_service = ThumbnailService()

    async def scan_video(self, video: Video) -> Video:
        """
        Extract metadata and generate a thumbnail for a single video.

        Updates the video record in-place and flushes to the database.
        """
        loop = asyncio.get_running_loop()

        try:
            # Extract metadata in executor
            meta = await loop.run_in_executor(
                None, extract_video_metadata, video.project_path
            )

            video.duration = meta.duration
            video.fps = meta.fps
            video.width = meta.width
            video.height = meta.height
            video.resolution = meta.resolution
            video.codec = meta.codec
            video.bitrate = meta.bitrate
            video.size_bytes = meta.size_bytes or video.size_bytes

            # Generate thumbnail in executor
            thumbnail_path = await loop.run_in_executor(
                None,
                self.thumbnail_service.generate_thumbnail,
                video.project_path,
                video.id,
            )
            video.thumbnail_path = thumbnail_path
            video.status = "scanned"

        except Exception as exc:
            video.status = "error"
            video.notes = f"Scan error: {str(exc)}"

        await self.session.flush()
        await self.session.refresh(video)
        return video

    async def scan_pending(
        self, project_id: str | None = None
    ) -> list[Video]:
        """
        Scan all pending videos, optionally filtered by project.

        Returns the list of scanned videos.
        """
        pending = await self.repo.get_pending_videos(project_id)
        scanned: list[Video] = []

        for video in pending:
            result = await self.scan_video(video)
            scanned.append(result)

        return scanned

    async def rescan_video(self, video_id: str) -> Video | None:
        """Force a rescan of a single video regardless of status."""
        video = await self.repo.get_by_id(video_id)
        if not video:
            return None
        video.status = "pending"
        return await self.scan_video(video)
