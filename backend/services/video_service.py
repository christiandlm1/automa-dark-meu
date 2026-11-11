"""
AUTOMA Services - Video Service.

Business logic for importing, managing, and querying videos.
"""

import asyncio
import uuid
from pathlib import Path
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.video import Video
from repositories.video_repository import VideoRepository
from repositories.project_repository import ProjectRepository
from schemas.video import VideoCreate, VideoUpdate, VideoImportRequest
from utils.file_utils import (
    compute_file_hash,
    get_file_size,
    is_valid_video_extension,
    safe_copy_file,
)
from utils.video_utils import strip_video_metadata


class VideoService:
    """Encapsulates all business rules related to videos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VideoRepository(session)
        self.project_repo = ProjectRepository(session)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    async def import_videos(
        self, request: VideoImportRequest
    ) -> list[Video]:
        """
        Import one or more video files into a project.

        Validates extensions, optionally copies files, creates DB records,
        and computes hashes in a thread pool executor.
        """
        project = await self.project_repo.get_by_id(request.project_id)
        if not project:
            raise ValueError(f"Project not found: {request.project_id}")

        imported: list[Video] = []
        loop = asyncio.get_running_loop()

        for file_path in request.file_paths:
            source = Path(file_path)

            # Validate extension
            if not is_valid_video_extension(str(source)):
                continue  # skip unsupported files silently

            if not source.is_file():
                continue  # skip missing files

            # Determine destination path
            if request.copy_to_project:
                dest_dir = Path(project.path) / "videos"
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = str(dest_dir / source.name)
                # Copy in executor (IO-bound)
                await loop.run_in_executor(
                    None, safe_copy_file, str(source), dest_path
                )
                project_path = dest_path
                await loop.run_in_executor(None, strip_video_metadata, project_path)
            else:
                project_path = str(source)

            # Get file size
            size_bytes = await loop.run_in_executor(
                None, get_file_size, project_path
            )

            # Compute hash in executor (CPU-bound)
            file_hash = await loop.run_in_executor(
                None, compute_file_hash, project_path
            )

            # Check for duplicates by hash
            existing = await self.repo.get_by_hash(file_hash)
            if existing and existing.project_id == request.project_id:
                continue  # already imported in this project

            video = Video(
                id=str(uuid.uuid4()),
                project_id=request.project_id,
                name=source.name,
                original_path=str(source),
                project_path=project_path,
                size_bytes=size_bytes,
                hash=file_hash,
                status="pending",
            )

            created = await self.repo.create(video)
            imported.append(created)

        return imported

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def create_video(self, data: VideoCreate) -> Video:
        """Create a video record directly (without import workflow)."""
        video = Video(
            id=str(uuid.uuid4()),
            project_id=data.project_id,
            name=data.name,
            original_path=data.original_path,
            project_path=data.project_path,
            size_bytes=data.size_bytes,
        )
        return await self.repo.create(video)

    async def get_video(self, video_id: str) -> Video | None:
        """Get a single video by ID."""
        return await self.repo.get_by_id(video_id)

    async def list_videos(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Video], int]:
        """List videos for a project with count."""
        videos = await self.repo.get_by_project(
            project_id, skip=skip, limit=limit
        )
        total = await self.repo.count_by_project(project_id)
        return videos, total

    async def update_video(
        self, video_id: str, data: VideoUpdate
    ) -> Video | None:
        """Update video metadata."""
        video = await self.repo.get_by_id(video_id)
        if not video:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(video, update_data)

    async def delete_video(self, video_id: str) -> bool:
        """Delete a video record."""
        return await self.repo.delete_by_id(video_id)

    async def get_pending_videos(
        self, project_id: str | None = None
    ) -> Sequence[Video]:
        """Get videos pending scan."""
        return await self.repo.get_pending_videos(project_id)
