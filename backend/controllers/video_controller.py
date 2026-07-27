"""
AUTOMA Controllers - Video Controller.

Thin controller that delegates to VideoService and ScannerService.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.video import (
    VideoImportRequest,
    VideoListResponse,
    VideoResponse,
    VideoUpdate,
)
from services.video_service import VideoService
from services.scanner_service import ScannerService
from services.log_service import LogService


class VideoController:
    """Handles HTTP request/response translation for video endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.service = VideoService(session)
        self.scanner = ScannerService(session)
        self.log_service = LogService(session)

    async def import_videos(
        self, data: VideoImportRequest
    ) -> list[VideoResponse]:
        """Import one or more video files into a project."""
        try:
            videos = await self.service.import_videos(data)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        await self.log_service.log_info(
            action="import",
            message=f"Imported {len(videos)} video(s)",
            project_id=data.project_id,
            details={"file_paths": data.file_paths},
        )

        return [VideoResponse.model_validate(v) for v in videos]

    async def get(self, video_id: str) -> VideoResponse:
        """Get a single video by ID."""
        video = await self.service.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )
        return VideoResponse.model_validate(video)

    async def list_by_project(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> VideoListResponse:
        """List videos in a project."""
        videos, total = await self.service.list_videos(
            project_id, skip=skip, limit=limit
        )
        return VideoListResponse(
            videos=[VideoResponse.model_validate(v) for v in videos],
            total=total,
        )

    async def update(
        self, video_id: str, data: VideoUpdate
    ) -> VideoResponse:
        """Update video metadata."""
        video = await self.service.update_video(video_id, data)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )
        return VideoResponse.model_validate(video)

    async def delete(self, video_id: str) -> dict[str, str]:
        """Delete a video."""
        success = await self.service.delete_video(video_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )
        await self.log_service.log_info(
            action="delete",
            message=f"Video deleted: {video_id}",
        )
        return {"detail": "Video deleted successfully"}

    async def scan_video(self, video_id: str) -> VideoResponse:
        """Scan/rescan a single video for metadata and thumbnail."""
        video = await self.scanner.rescan_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )
        await self.log_service.log_info(
            action="scan",
            message=f"Video scanned: {video.name}",
            project_id=video.project_id,
        )
        return VideoResponse.model_validate(video)

    async def scan_pending(
        self, project_id: str | None = None
    ) -> list[VideoResponse]:
        """Scan all pending videos, optionally in a specific project."""
        scanned = await self.scanner.scan_pending(project_id)
        return [VideoResponse.model_validate(v) for v in scanned]
